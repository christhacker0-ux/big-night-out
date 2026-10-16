using System;
using System.IO;
using System.Linq;
using BigNightOut.Core;
using BigNightOut.Interaction;
using BigNightOut.Inventory;
using BigNightOut.Rooms;
using BigNightOut.UI;
using TMPro;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.UI;
using Object = UnityEngine.Object;

namespace BigNightOut.EditorTools
{
    /// <summary>
    /// Big Night Out > Build Dorm Hallway Slice.
    /// Creates placeholder art, item and room assets, the DexRoom and DormHallway room scenes and the Boot scene,
    /// wires every reference, and adds the scenes to the build. Safe to run again: it overwrites
    /// the generated files, so do not hand-edit them until the real art arrives.
    /// </summary>
    public static class SliceBuilder
    {
        const string Root = "Assets/_Project";
        const string PlaceholderFolder = Root + "/Art/Placeholder";
        const string ItemFolder = Root + "/Data/Items";
        const string RoomFolder = Root + "/Data/Rooms";
        const string PrefabFolder = Root + "/Prefabs";
        const string BootPath = Root + "/Scenes/Boot.unity";
        const string HallwayPath = Root + "/Scenes/Rooms/DormHallway.unity";
        const string DexRoomPath = Root + "/Scenes/Rooms/DexRoom.unity";

        static readonly (string id, string name, Color color)[] Items =
        {
            ("earplugs", "Earplugs", new Color(1f, 0.85f, 0.2f)),
            ("dance_album", "Hank Hollister Live", new Color(0.6f, 0.3f, 0.1f)),
            ("lemon", "Lemon", new Color(1f, 0.95f, 0.3f)),
            ("soda", "Soda", new Color(0.3f, 0.7f, 1f)),
            ("hallway_hooch", "Hallway Hooch", new Color(0.9f, 0.5f, 0.2f)),
            ("cowboy_hat", "Cowboy Hat", new Color(0.55f, 0.35f, 0.2f)),
            ("dollar", "Crumpled Dollar", new Color(0.45f, 0.75f, 0.4f)),
        };

        [MenuItem("Big Night Out/Build Dorm Hallway Slice")]
        public static void Build()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;

            foreach (var folder in new[] { PlaceholderFolder, ItemFolder, RoomFolder, PrefabFolder, Root + "/Scenes/Rooms" })
                EnsureFolder(folder);

            var database = BuildItems();
            var dexRoom = BuildRoomDefinition("dex_room", "DexRoom");
            var hallway = BuildRoomDefinition("dorm_hallway", "DormHallway");
            BuildDexRoomScene(dexRoom);
            BuildHallwayScene(hallway);
            var slotPrefab = BuildSlotPrefab();
            BuildBootScene(new[] { dexRoom, hallway }, dexRoom, database, slotPrefab);

            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(BootPath, true),
                new EditorBuildSettingsScene(DexRoomPath, true),
                new EditorBuildSettingsScene(HallwayPath, true),
            };

            EditorSceneManager.OpenScene(BootPath);
            Debug.Log("Dorm Hallway slice built. Press Play in the Boot scene.");
        }

        // ---------- Data ----------

        static ItemDatabase BuildItems()
        {
            var database = LoadOrCreate<ItemDatabase>($"{ItemFolder}/ItemDatabase.asset");
            var so = new SerializedObject(database);
            var list = so.FindProperty("items");
            list.ClearArray();

            foreach (var (id, displayName, color) in Items)
            {
                var item = LoadOrCreate<ItemDefinition>($"{ItemFolder}/Item_{id}.asset");
                var itemSo = new SerializedObject(item);
                itemSo.FindProperty("id").stringValue = id;
                itemSo.FindProperty("displayName").stringValue = displayName;
                itemSo.FindProperty("icon").objectReferenceValue = PlaceholderSprite($"icon_{id}", 64, 64, color, 64, false);
                itemSo.FindProperty("lookNode").stringValue = $"Item_{id}_Look";
                itemSo.ApplyModifiedPropertiesWithoutUndo();

                list.InsertArrayElementAtIndex(list.arraySize);
                list.GetArrayElementAtIndex(list.arraySize - 1).objectReferenceValue = item;
            }

            var combos = so.FindProperty("combinations");
            combos.ClearArray();
            combos.InsertArrayElementAtIndex(0);
            var combo = combos.GetArrayElementAtIndex(0);
            combo.FindPropertyRelative("itemA").stringValue = "lemon";
            combo.FindPropertyRelative("itemB").stringValue = "soda";
            combo.FindPropertyRelative("node").stringValue = "Combine_Lemon_Soda";

            so.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(database);
            AssetDatabase.SaveAssets();
            return database;
        }

        static RoomDefinition BuildRoomDefinition(string id, string sceneName)
        {
            var room = LoadOrCreate<RoomDefinition>($"{RoomFolder}/Room_{id}.asset");
            var so = new SerializedObject(room);
            so.FindProperty("id").stringValue = id;
            so.FindProperty("sceneName").stringValue = sceneName;
            so.ApplyModifiedPropertiesWithoutUndo();
            AssetDatabase.SaveAssets();
            return room;
        }

        // ---------- Room scene ----------

        static void BuildDexRoomScene(RoomDefinition definition)
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = AddRoomShell("DexRoom", definition, "DexRoom_Enter", new Color(0.3f, 0.4f, 0.45f), new Color(0.4f, 0.32f, 0.25f));
            AddEntry(root, "start", new Vector2(-2f, -4f), false);
            AddEntry(root, "from_hallway", new Vector2(6.4f, -4f), true);

            AddHotspot(root, "Bed", new Vector2(-5.5f, -3.4f), new Vector2(3f, 1.2f), new Color(0.7f, 0.25f, 0.3f),
                new Vector2(-3.6f, -4.2f), true, "Bed_Look", "Bed_Use");
            AddHotspot(root, "Mirror", new Vector2(-1.2f, -1.2f), new Vector2(1f, 1.6f), new Color(0.75f, 0.85f, 0.9f),
                new Vector2(-1.2f, -3.4f), false, "Mirror_Look", "Mirror_Use");
            AddHotspot(root, "Desk", new Vector2(2.2f, -2.8f), new Vector2(2f, 1.4f), new Color(0.55f, 0.4f, 0.25f),
                new Vector2(2.2f, -3.8f), false, "Desk_Look", "Desk_Use");
            AddHotspot(root, "Door to hallway", new Vector2(7.6f, -2.6f), new Vector2(1.4f, 3f), new Color(0.45f, 0.3f, 0.2f),
                new Vector2(6.6f, -3.6f), false, "DexDoor_Look", "DexDoor_Use");

            EditorSceneManager.SaveScene(scene, DexRoomPath);
        }

        static void BuildHallwayScene(RoomDefinition definition)
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = AddRoomShell("DormHallway", definition, "DormHallway_Enter", new Color(0.35f, 0.3f, 0.45f), new Color(0.45f, 0.35f, 0.3f));
            AddEntry(root, "start", new Vector2(-7f, -4f), false);
            AddEntry(root, "from_room", new Vector2(-7f, -4f), false);

            AddHotspot(root, "Your door", new Vector2(-8.2f, -2.6f), new Vector2(1.2f, 3f), new Color(0.45f, 0.3f, 0.2f),
                new Vector2(-7.4f, -3.6f), true, "HallDoor_Look", "HallDoor_Use");
            AddHotspot(root, "Lacey Rae", new Vector2(-2f, -2.8f), new Vector2(1f, 2.6f), new Color(0.95f, 0.5f, 0.65f),
                new Vector2(-3.2f, -3.4f), false, "Lacey_Look", "Lacey_Talk",
                ("dance_album", "Lacey_GiveAlbum"), ("hallway_hooch", "Lacey_GiveDrink"));
            AddHotspot(root, "Gil", new Vector2(5f, -2.7f), new Vector2(1f, 2.4f), new Color(0.4f, 0.55f, 0.95f),
                new Vector2(3.8f, -3.4f), false, "Gil_Look", "Gil_Talk",
                ("earplugs", "Gil_GiveEarplugs"));
            AddHotspot(root, "Vending machine", new Vector2(7.6f, -2.6f), new Vector2(1.4f, 3f), new Color(0.6f, 0.6f, 0.65f),
                new Vector2(6.6f, -3.6f), false, "Vending_Look", "Vending_Use",
                ("dollar", "Vending_Use"));
            AddHotspot(root, "Drinks table", new Vector2(1.5f, -3.3f), new Vector2(2.2f, 1f), new Color(0.5f, 0.3f, 0.2f),
                new Vector2(1.5f, -4.2f), false, "DrinksTable_Look", "DrinksTable_Use");

            EditorSceneManager.SaveScene(scene, HallwayPath);
        }

        /// <summary>The parts every room has: Room component, background, floor and walkable area.</summary>
        static Transform AddRoomShell(string name, RoomDefinition definition, string onEnterNode, Color wall, Color floorColor)
        {
            var root = new GameObject(name);
            var room = root.AddComponent<Room>();
            Set(room, "definition", definition);
            SetString(room, "onEnterNode", onEnterNode);

            // Background: 19.2 x 10.8 units fills a 1080p screen at camera size 5.4.
            var background = AddSprite(root.transform, "Background", PlaceholderSprite($"bg_{definition.Id}", 192, 108, wall, 10, false), Vector2.zero);
            background.sortingOrder = -10000;
            var floor = AddSprite(root.transform, "FloorPaint", PlaceholderSprite($"bg_{definition.Id}_floor", 192, 30, floorColor, 10, false), new Vector2(0f, -3.9f));
            floor.sortingOrder = -9999;

            var walkable = new GameObject("WalkableArea");
            walkable.transform.SetParent(root.transform, false);
            var polygon = walkable.AddComponent<PolygonCollider2D>();
            polygon.isTrigger = true;
            polygon.points = new[] { new Vector2(-9f, -5f), new Vector2(9f, -5f), new Vector2(8.5f, -2.6f), new Vector2(-8.5f, -2.6f) };
            walkable.AddComponent<WalkableArea>();

            return root.transform;
        }

        static void AddEntry(Transform parent, string entryName, Vector2 position, bool faceLeft)
        {
            var entry = new GameObject($"Entry_{entryName}");
            entry.transform.SetParent(parent, false);
            entry.transform.position = position;
            var point = entry.AddComponent<EntryPoint>();
            SetString(point, "entryName", entryName);
            SetBool(point, "faceLeft", faceLeft);
        }

        static void AddHotspot(Transform parent, string displayName, Vector2 feet, Vector2 size, Color color,
            Vector2 standAt, bool faceLeft, string lookNode, string useNode, params (string item, string node)[] itemNodes)
        {
            var slug = displayName.ToLowerInvariant().Replace(' ', '_');
            var go = new GameObject($"Hotspot_{slug}");
            go.transform.SetParent(parent, false);
            go.transform.position = feet;

            var sprite = go.AddComponent<SpriteRenderer>();
            sprite.sprite = PlaceholderSprite($"hs_{slug}", Mathf.RoundToInt(size.x * 32), Mathf.RoundToInt(size.y * 32), color, 32, true);
            var sorter = go.AddComponent<SortByY>();
            SetBool(sorter, "everyFrame", false);

            var box = go.AddComponent<BoxCollider2D>();
            box.isTrigger = true;
            box.size = size;
            box.offset = new Vector2(0f, size.y / 2f);

            var stand = new GameObject("WalkTo");
            stand.transform.SetParent(go.transform, false);
            stand.transform.position = standAt;

            var hotspot = go.AddComponent<Hotspot>();
            var so = new SerializedObject(hotspot);
            so.FindProperty("displayName").stringValue = displayName;
            so.FindProperty("walkTo").objectReferenceValue = stand.transform;
            so.FindProperty("faceLeftOnArrival").boolValue = faceLeft;
            so.FindProperty("lookNode").stringValue = lookNode;
            so.FindProperty("useNode").stringValue = useNode;
            var list = so.FindProperty("itemNodes");
            list.ClearArray();
            foreach (var (item, node) in itemNodes)
            {
                list.InsertArrayElementAtIndex(list.arraySize);
                var element = list.GetArrayElementAtIndex(list.arraySize - 1);
                element.FindPropertyRelative("itemId").stringValue = item;
                element.FindPropertyRelative("node").stringValue = node;
            }
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        // ---------- Boot scene ----------

        static InventorySlot BuildSlotPrefab()
        {
            var go = new GameObject("InventorySlot", typeof(RectTransform));
            ((RectTransform)go.transform).sizeDelta = new Vector2(72f, 72f);
            var background = go.AddComponent<Image>();
            background.color = new Color(0f, 0f, 0f, 0.4f);

            var highlight = new GameObject("Held", typeof(RectTransform));
            highlight.transform.SetParent(go.transform, false);
            Stretch((RectTransform)highlight.transform, 0f);
            highlight.AddComponent<Image>().color = new Color(1f, 0.85f, 0.3f, 0.6f);

            var icon = new GameObject("Icon", typeof(RectTransform));
            icon.transform.SetParent(go.transform, false);
            Stretch((RectTransform)icon.transform, 6f);
            var iconImage = icon.AddComponent<Image>();
            iconImage.raycastTarget = false;

            var slot = go.AddComponent<InventorySlot>();
            Set(slot, "icon", iconImage);
            Set(slot, "heldHighlight", highlight);

            var prefab = PrefabUtility.SaveAsPrefabAsset(go, $"{PrefabFolder}/InventorySlot.prefab");
            Object.DestroyImmediate(go);
            return prefab.GetComponent<InventorySlot>();
        }

        static void BuildBootScene(RoomDefinition[] allRooms, RoomDefinition firstRoom, ItemDatabase database, InventorySlot slotPrefab)
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var cameraGo = new GameObject("Main Camera");
            cameraGo.tag = "MainCamera";
            var camera = cameraGo.AddComponent<Camera>();
            camera.orthographic = true;
            camera.orthographicSize = 5.4f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.black;
            cameraGo.transform.position = new Vector3(0f, 0f, -10f);

            // Player
            var player = new GameObject("Player");
            var mover = player.AddComponent<PlayerMover>();
            var visual = new GameObject("Visual");
            visual.transform.SetParent(player.transform, false);
            var body = visual.AddComponent<SpriteRenderer>();
            body.sprite = PlaceholderSprite("player_dex", 32, 80, new Color(0.3f, 0.85f, 0.4f), 32, true);
            visual.AddComponent<SortByY>();
            Set(mover, "visual", visual.transform);

            // Game
            var game = new GameObject("Game");
            var loader = game.AddComponent<RoomLoader>();
            var loaderSo = new SerializedObject(loader);
            var rooms = loaderSo.FindProperty("rooms");
            rooms.ClearArray();
            foreach (var room in allRooms)
            {
                rooms.InsertArrayElementAtIndex(rooms.arraySize);
                rooms.GetArrayElementAtIndex(rooms.arraySize - 1).objectReferenceValue = room;
            }
            loaderSo.FindProperty("player").objectReferenceValue = mover;
            loaderSo.ApplyModifiedPropertiesWithoutUndo();

            var manager = game.AddComponent<GameManager>();
            Set(manager, "roomLoader", loader);
            Set(manager, "firstRoom", firstRoom);
            SetString(manager, "firstEntry", "start");

            // UI
            var canvasGo = new GameObject("Canvas", typeof(RectTransform));
            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            var scaler = canvasGo.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920f, 1080f);
            canvasGo.AddComponent<GraphicRaycaster>();

            var labelRoot = new GameObject("HoverLabel", typeof(RectTransform));
            labelRoot.transform.SetParent(canvasGo.transform, false);
            var labelRect = (RectTransform)labelRoot.transform;
            labelRect.sizeDelta = new Vector2(600f, 50f);
            var text = labelRoot.AddComponent<TextMeshProUGUI>();
            text.alignment = TextAlignmentOptions.Center;
            text.fontSize = 32f;
            text.raycastTarget = false;
            var hover = labelRoot.AddComponent<HoverLabel>();
            Set(hover, "label", text);
            Set(hover, "root", labelRect);

            var bar = new GameObject("InventoryBar", typeof(RectTransform));
            bar.transform.SetParent(canvasGo.transform, false);
            var barRect = (RectTransform)bar.transform;
            barRect.anchorMin = new Vector2(0f, 1f);
            barRect.anchorMax = new Vector2(1f, 1f);
            barRect.pivot = new Vector2(0.5f, 1f);
            barRect.sizeDelta = new Vector2(0f, 88f);
            barRect.anchoredPosition = Vector2.zero;
            var layout = bar.AddComponent<HorizontalLayoutGroup>();
            layout.spacing = 8f;
            layout.padding = new RectOffset(8, 8, 8, 8);
            layout.childAlignment = TextAnchor.UpperLeft;
            layout.childControlWidth = false;
            layout.childControlHeight = false;
            layout.childForceExpandWidth = false;
            layout.childForceExpandHeight = false;
            var inventory = bar.AddComponent<InventoryBar>();
            Set(inventory, "database", database);
            Set(inventory, "slotPrefab", slotPrefab);
            Set(inventory, "slotParent", bar.transform);

            AddPauseMenu(canvasGo.transform);

            // Input
            var input = new GameObject("Input");
            var pointer = input.AddComponent<PointerController>();
            Set(pointer, "worldCamera", camera);
            Set(pointer, "player", mover);
            Set(pointer, "hoverLabel", hover);

            AddYarn();
            EnsureOneEventSystem();

            EditorSceneManager.SaveScene(scene, BootPath);
        }

        /// <summary>A full-screen dimmer with Resume, Save, Load and Quit, hidden until Esc.</summary>
        static void AddPauseMenu(Transform canvas)
        {
            var menuGo = new GameObject("PauseMenu", typeof(RectTransform));
            menuGo.transform.SetParent(canvas, false);
            Stretch((RectTransform)menuGo.transform, 0f);

            var panel = new GameObject("Panel", typeof(RectTransform));
            panel.transform.SetParent(menuGo.transform, false);
            Stretch((RectTransform)panel.transform, 0f);
            panel.AddComponent<Image>().color = new Color(0f, 0f, 0f, 0.75f);

            var column = new GameObject("Buttons", typeof(RectTransform));
            column.transform.SetParent(panel.transform, false);
            ((RectTransform)column.transform).sizeDelta = new Vector2(400f, 420f);
            var layout = column.AddComponent<VerticalLayoutGroup>();
            layout.spacing = 16f;
            layout.childAlignment = TextAnchor.MiddleCenter;
            layout.childControlWidth = true;
            layout.childControlHeight = false;
            layout.childForceExpandWidth = true;
            layout.childForceExpandHeight = false;

            var title = AddText(column.transform, "Title", "Paused", 56f);
            ((RectTransform)title.transform).sizeDelta = new Vector2(400f, 80f);
            var resume = AddButton(column.transform, "Resume");
            var save = AddButton(column.transform, "Save");
            var load = AddButton(column.transform, "Load");
            var quit = AddButton(column.transform, "Quit");
            var status = AddText(column.transform, "Status", "", 28f);
            ((RectTransform)status.transform).sizeDelta = new Vector2(400f, 40f);

            var menu = menuGo.AddComponent<PauseMenu>();
            Set(menu, "panel", panel);
            Set(menu, "resumeButton", resume);
            Set(menu, "saveButton", save);
            Set(menu, "loadButton", load);
            Set(menu, "quitButton", quit);
            Set(menu, "status", status);
        }

        static Button AddButton(Transform parent, string label)
        {
            var go = new GameObject($"Button_{label}", typeof(RectTransform));
            go.transform.SetParent(parent, false);
            ((RectTransform)go.transform).sizeDelta = new Vector2(400f, 64f);
            go.AddComponent<Image>().color = new Color(0.25f, 0.2f, 0.35f);
            var button = go.AddComponent<Button>();
            var text = AddText(go.transform, "Label", label, 32f);
            Stretch((RectTransform)text.transform, 0f);
            text.raycastTarget = false;
            return button;
        }

        static TextMeshProUGUI AddText(Transform parent, string name, string value, float size)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            var text = go.AddComponent<TextMeshProUGUI>();
            text.text = value;
            text.fontSize = size;
            text.alignment = TextAlignmentOptions.Center;
            return text;
        }

        /// <summary>Yarn's prefab brings its own EventSystem; add one only if it didn't, and make it use the Input System.</summary>
        static void EnsureOneEventSystem()
        {
            var eventSystem = Object.FindFirstObjectByType<EventSystem>(FindObjectsInactive.Include);
            if (eventSystem == null)
            {
                eventSystem = new GameObject("EventSystem").AddComponent<EventSystem>();
            }
            foreach (var module in eventSystem.GetComponents<BaseInputModule>())
            {
                if (!(module is InputSystemUIInputModule))
                {
                    Object.DestroyImmediate(module);
                }
            }
            if (eventSystem.GetComponent<InputSystemUIInputModule>() == null)
            {
                eventSystem.gameObject.AddComponent<InputSystemUIInputModule>();
            }
        }

        /// <summary>Adds Yarn Spinner's dialogue prefab and our starter, if Yarn is installed.</summary>
        static void AddYarn()
        {
            var starterType = Type.GetType("BigNightOut.YarnBridge.YarnDialogueStarter, BigNightOut.Yarn");
            if (starterType == null)
            {
                Debug.LogWarning("Yarn Spinner is not installed, so the Boot scene has no dialogue yet. Install it (see README) and run this again.");
                return;
            }

            var prefabPath = AssetDatabase.FindAssets("Dialogue System t:Prefab")
                .Select(AssetDatabase.GUIDToAssetPath)
                .FirstOrDefault(path => Path.GetFileNameWithoutExtension(path) == "Dialogue System");
            if (prefabPath == null)
            {
                Debug.LogWarning("Could not find Yarn Spinner's 'Dialogue System' prefab. Add it to the Boot scene by hand, then add YarnDialogueStarter next to the Dialogue Runner.");
                return;
            }

            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(prefabPath);
            var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            var runner = instance.GetComponentsInChildren<MonoBehaviour>(true).FirstOrDefault(c => c != null && c.GetType().Name == "DialogueRunner");
            if (runner == null)
            {
                Debug.LogWarning("The Yarn prefab has no Dialogue Runner; add YarnDialogueStarter by hand.");
                return;
            }
            runner.gameObject.AddComponent(starterType);

            var projectGuid = AssetDatabase.FindAssets("t:YarnProject").FirstOrDefault();
            if (projectGuid == null)
            {
                Debug.LogWarning("No Yarn Project found. Assets/_Project/Dialogue/BigNightOut.yarnproject should be there; if Unity did not import it, right-click it and choose Reimport.");
                return;
            }
            var runnerSo = new SerializedObject(runner);
            var projectProperty = runnerSo.FindProperty("yarnProject");
            if (projectProperty == null)
            {
                Debug.LogWarning("Assign the Yarn Project to the Dialogue Runner by hand.");
                return;
            }
            projectProperty.objectReferenceValue = AssetDatabase.LoadMainAssetAtPath(AssetDatabase.GUIDToAssetPath(projectGuid));
            runnerSo.ApplyModifiedPropertiesWithoutUndo();
        }

        // ---------- Helpers ----------

        static SpriteRenderer AddSprite(Transform parent, string name, Sprite sprite, Vector2 position)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.position = position;
            var renderer = go.AddComponent<SpriteRenderer>();
            renderer.sprite = sprite;
            return renderer;
        }

        /// <summary>A flat-colour PNG with a darker border, imported as a sprite.</summary>
        static Sprite PlaceholderSprite(string name, int width, int height, Color color, float pixelsPerUnit, bool pivotAtFeet)
        {
            var path = $"{PlaceholderFolder}/{name}.png";
            var texture = new Texture2D(width, height, TextureFormat.RGBA32, false);
            var border = color * 0.6f;
            border.a = 1f;
            var pixels = new Color[width * height];
            for (var y = 0; y < height; y++)
            for (var x = 0; x < width; x++)
            {
                var edge = x < 2 || y < 2 || x >= width - 2 || y >= height - 2;
                pixels[y * width + x] = edge ? border : color;
            }
            texture.SetPixels(pixels);
            texture.Apply();
            File.WriteAllBytes(path, texture.EncodeToPNG());
            Object.DestroyImmediate(texture);
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate);

            var importer = (TextureImporter)AssetImporter.GetAtPath(path);
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.spritePixelsPerUnit = pixelsPerUnit;
            importer.filterMode = FilterMode.Point;
            var settings = new TextureImporterSettings();
            importer.ReadTextureSettings(settings);
            settings.spriteAlignment = (int)(pivotAtFeet ? SpriteAlignment.BottomCenter : SpriteAlignment.Center);
            importer.SetTextureSettings(settings);
            importer.SaveAndReimport();

            return AssetDatabase.LoadAssetAtPath<Sprite>(path);
        }

        static T LoadOrCreate<T>(string path) where T : ScriptableObject
        {
            var asset = AssetDatabase.LoadAssetAtPath<T>(path);
            if (asset != null) return asset;
            asset = ScriptableObject.CreateInstance<T>();
            AssetDatabase.CreateAsset(asset, path);
            return asset;
        }

        static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            var parent = Path.GetDirectoryName(path)?.Replace('\\', '/');
            if (!string.IsNullOrEmpty(parent)) EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }

        static void Stretch(RectTransform rect, float inset)
        {
            rect.anchorMin = Vector2.zero;
            rect.anchorMax = Vector2.one;
            rect.offsetMin = new Vector2(inset, inset);
            rect.offsetMax = new Vector2(-inset, -inset);
        }

        static void Set(Object target, string field, Object value)
        {
            var so = new SerializedObject(target);
            so.FindProperty(field).objectReferenceValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        static void SetString(Object target, string field, string value)
        {
            var so = new SerializedObject(target);
            so.FindProperty(field).stringValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        static void SetBool(Object target, string field, bool value)
        {
            var so = new SerializedObject(target);
            so.FindProperty(field).boolValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }
    }
}
