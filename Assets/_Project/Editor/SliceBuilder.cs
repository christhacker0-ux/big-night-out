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
    /// Big Night Out > Build Game (also still under its old name, Build Dorm Hallway Slice).
    /// Reads every World/*.json file (items, item combinations, rooms and their hotspots),
    /// creates the item and room assets, one scene per room and the Boot scene, wires every
    /// reference, and adds the scenes to the build. Safe to run again: it overwrites the
    /// generated files, so change the JSON and Yarn files rather than the scenes.
    /// </summary>
    public static class SliceBuilder
    {
        const string Root = "Assets/_Project";
        const string PlaceholderFolder = Root + "/Art/Placeholder";
        // Finished art. A PNG here named like a placeholder (bg_dex_room, hs_gil, icon_lemon,
        // player_dex) replaces it on the next build. 100 pixels = 1 unit; a room is 1920x1080.
        const string PaintedFolder = Root + "/Art/Painted";
        // True while building a room whose background is painted: its props are in the
        // painting, so hotspots without their own painted sprite stay invisible.
        static bool roomIsPainted;
        // Under Resources so a built game can still find rooms and items if a scene reference is lost.
        const string ItemFolder = Root + "/Resources/Items";
        const string RoomFolder = Root + "/Resources/Rooms";
        const string PrefabFolder = Root + "/Prefabs";
        const string BootPath = Root + "/Scenes/Boot.unity";
        const string RoomSceneFolder = Root + "/Scenes/Rooms";
        const string WorldFolder = Root + "/World";
        const string FirstRoomId = "dex_room";

        [MenuItem("Big Night Out/Build Game")]
        public static void Build()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;

            foreach (var folder in new[] { PlaceholderFolder, ItemFolder, RoomFolder, PrefabFolder, RoomSceneFolder })
                EnsureFolder(folder);

            var world = LoadWorld();
            BuildItems(world);
            foreach (var room in world.rooms) BuildRoomDefinition(room.id, room.scene);
            foreach (var room in world.rooms) BuildRoomScene(room);
            BuildSlotPrefab();
            if (Painted("player_dex", true) == null)
                PlaceholderSprite("player_dex", 32, 80, new Color(0.3f, 0.85f, 0.4f), 32, true);

            // Reload every asset by path right before wiring it: importing the placeholder sprites can
            // leave earlier in-memory copies stale, and a stale copy is saved as an empty reference.
            AssetDatabase.SaveAssets();
            var rooms = world.rooms.Select(r => RoomAsset(r.id)).ToArray();
            var database = AssetDatabase.LoadAssetAtPath<ItemDatabase>(DatabasePath);
            var slotPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(SlotPrefabPath).GetComponent<InventorySlot>();
            BuildBootScene(rooms, RoomAsset(FirstRoomId) ?? rooms[0], database, slotPrefab);

            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(BootPath, true) }
                .Concat(world.rooms.Select(r => new EditorBuildSettingsScene(RoomScenePath(r.scene), true)))
                .ToArray();

            EditorSceneManager.OpenScene(BootPath);
            Debug.Log($"Big Night Out built: {world.rooms.Count} rooms, {world.items.Count} items. Press Play in the Boot scene.");
        }

        // The old menu name, kept so existing instructions still work.
        [MenuItem("Big Night Out/Build Dorm Hallway Slice")]
        public static void BuildOldName() => Build();

        static string RoomScenePath(string scene) => $"{RoomSceneFolder}/{scene}.unity";

        // ---------- World files ----------
        // JsonUtility can't read Vector2 from [x, y], so positions are float arrays.

        [Serializable] public class ItemSpec { public string id; public string name; public float[] color; }
        [Serializable] public class ComboSpec { public string a; public string b; public string node; }
        [Serializable] public class EntrySpec { public string name; public float[] pos; public bool faceLeft; }
        [Serializable] public class ItemNodeSpec { public string item; public string node; }
        [Serializable] public class HotspotSpec
        {
            public string name;
            public float[] feet;
            public float[] size;
            public float[] color;
            public float[] standAt;
            public bool faceLeft;
            public string look;
            public string use;
            public ItemNodeSpec[] items;
            public string hideWhenFlag;
            public string showWhenFlag;
        }
        [Serializable] public class RoomSpec
        {
            public string id;
            public string scene;
            public string onEnter;
            public float[] wall;
            public float[] floor;
            // Flat list of x, y pairs. Empty means the standard floor strip.
            public float[] walkable;
            public EntrySpec[] entries;
            public HotspotSpec[] hotspots;
        }
        [Serializable] public class WorldFile
        {
            public ItemSpec[] items;
            public ComboSpec[] combinations;
            public RoomSpec[] rooms;
        }

        public class World
        {
            public readonly System.Collections.Generic.List<ItemSpec> items = new System.Collections.Generic.List<ItemSpec>();
            public readonly System.Collections.Generic.List<ComboSpec> combinations = new System.Collections.Generic.List<ComboSpec>();
            public readonly System.Collections.Generic.List<RoomSpec> rooms = new System.Collections.Generic.List<RoomSpec>();
        }

        static World LoadWorld()
        {
            var world = new World();
            foreach (var path in Directory.GetFiles(WorldFolder, "*.json").OrderBy(p => p))
            {
                var file = JsonUtility.FromJson<WorldFile>(File.ReadAllText(path));
                if (file == null) { Debug.LogError($"Could not read {path}."); continue; }
                if (file.items != null) world.items.AddRange(file.items);
                if (file.combinations != null) world.combinations.AddRange(file.combinations);
                if (file.rooms != null) world.rooms.AddRange(file.rooms);
            }
            if (world.rooms.Count == 0) throw new Exception($"No rooms found in {WorldFolder}/*.json.");
            return world;
        }

        static Vector2 V(float[] a, Vector2 fallback = default) => a != null && a.Length >= 2 ? new Vector2(a[0], a[1]) : fallback;
        static Color C(float[] a, Color fallback) => a != null && a.Length >= 3 ? new Color(a[0], a[1], a[2]) : fallback;

        const string DatabasePath = ItemFolder + "/ItemDatabase.asset";
        const string SlotPrefabPath = PrefabFolder + "/InventorySlot.prefab";

        static RoomDefinition RoomAsset(string id) => AssetDatabase.LoadAssetAtPath<RoomDefinition>($"{RoomFolder}/Room_{id}.asset");

        // ---------- Data ----------

        static void BuildItems(World world)
        {
            // Make every icon first, so no import happens while item references are being wired.
            foreach (var spec in world.items)
                if (Painted($"icon_{spec.id}", false) == null)
                    PlaceholderSprite($"icon_{spec.id}", 64, 64, C(spec.color, Color.gray), 64, false);

            foreach (var spec in world.items)
            {
                var item = LoadOrCreate<ItemDefinition>($"{ItemFolder}/Item_{spec.id}.asset");
                var itemSo = new SerializedObject(item);
                itemSo.FindProperty("id").stringValue = spec.id;
                itemSo.FindProperty("displayName").stringValue = spec.name;
                itemSo.FindProperty("icon").objectReferenceValue =
                    AssetDatabase.LoadAssetAtPath<Sprite>($"{PaintedFolder}/icon_{spec.id}.png") ??
                    AssetDatabase.LoadAssetAtPath<Sprite>($"{PlaceholderFolder}/icon_{spec.id}.png");
                itemSo.FindProperty("lookNode").stringValue = $"Item_{spec.id}_Look";
                itemSo.ApplyModifiedPropertiesWithoutUndo();
            }
            AssetDatabase.SaveAssets();

            var database = LoadOrCreate<ItemDatabase>(DatabasePath);
            var so = new SerializedObject(database);
            var list = so.FindProperty("items");
            list.ClearArray();
            foreach (var spec in world.items)
            {
                list.InsertArrayElementAtIndex(list.arraySize);
                list.GetArrayElementAtIndex(list.arraySize - 1).objectReferenceValue =
                    AssetDatabase.LoadAssetAtPath<ItemDefinition>($"{ItemFolder}/Item_{spec.id}.asset");
            }

            var combos = so.FindProperty("combinations");
            combos.ClearArray();
            foreach (var spec in world.combinations)
            {
                combos.InsertArrayElementAtIndex(combos.arraySize);
                var combo = combos.GetArrayElementAtIndex(combos.arraySize - 1);
                combo.FindPropertyRelative("itemA").stringValue = spec.a;
                combo.FindPropertyRelative("itemB").stringValue = spec.b;
                combo.FindPropertyRelative("node").stringValue = spec.node;
            }

            so.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(database);
            AssetDatabase.SaveAssets();
        }

        static void BuildRoomDefinition(string id, string sceneName)
        {
            var room = LoadOrCreate<RoomDefinition>($"{RoomFolder}/Room_{id}.asset");
            var so = new SerializedObject(room);
            so.FindProperty("id").stringValue = id;
            so.FindProperty("sceneName").stringValue = sceneName;
            so.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(room);
            AssetDatabase.SaveAssets();
        }

        // ---------- Room scene ----------

        static void BuildRoomScene(RoomSpec spec)
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = AddRoomShell(spec.scene, RoomAsset(spec.id), spec.onEnter,
                C(spec.wall, new Color(0.35f, 0.3f, 0.4f)), C(spec.floor, new Color(0.4f, 0.32f, 0.25f)), spec.walkable);
            foreach (var entry in spec.entries ?? new EntrySpec[0])
                AddEntry(root, entry.name, V(entry.pos), entry.faceLeft);
            foreach (var h in spec.hotspots ?? new HotspotSpec[0])
            {
                var feet = V(h.feet);
                var itemNodes = (h.items ?? new ItemNodeSpec[0]).Select(i => (i.item, i.node)).ToArray();
                var go = AddHotspot(root, h.name, feet, V(h.size, Vector2.one), C(h.color, Color.gray),
                    V(h.standAt, new Vector2(feet.x, -3.6f)), h.faceLeft, h.look, h.use, itemNodes);
                var so = new SerializedObject(go);
                so.FindProperty("hideWhenFlag").stringValue = h.hideWhenFlag ?? "";
                so.FindProperty("showWhenFlag").stringValue = h.showWhenFlag ?? "";
                so.ApplyModifiedPropertiesWithoutUndo();
            }
            EditorSceneManager.SaveScene(scene, RoomScenePath(spec.scene));
        }

        /// <summary>The parts every room has: Room component, background, floor and walkable area.</summary>
        static Transform AddRoomShell(string name, RoomDefinition definition, string onEnterNode, Color wall, Color floorColor, float[] walkablePoints)
        {
            var id = definition.Id;
            var root = new GameObject(name);

            // Background: 19.2 x 10.8 units fills a 1080p screen at camera size 5.4.
            var painted = Painted($"bg_{id}", false);
            roomIsPainted = painted != null;
            var background = AddSprite(root.transform, "Background", painted ?? PlaceholderSprite($"bg_{id}", 192, 108, wall, 10, false), Vector2.zero);
            background.sortingOrder = -10000;
            if (!roomIsPainted)
            {
                var floor = AddSprite(root.transform, "FloorPaint", PlaceholderSprite($"bg_{id}_floor", 192, 30, floorColor, 10, false), new Vector2(0f, -3.9f));
                floor.sortingOrder = -9999;
            }

            var room = root.AddComponent<Room>();
            Set(room, "definition", RoomAsset(id));
            SetString(room, "onEnterNode", onEnterNode);

            var walkable = new GameObject("WalkableArea");
            walkable.transform.SetParent(root.transform, false);
            var polygon = walkable.AddComponent<PolygonCollider2D>();
            polygon.isTrigger = true;
            polygon.points = walkablePoints != null && walkablePoints.Length >= 6
                ? Enumerable.Range(0, walkablePoints.Length / 2).Select(i => new Vector2(walkablePoints[2 * i], walkablePoints[2 * i + 1])).ToArray()
                : new[] { new Vector2(-9f, -5f), new Vector2(9f, -5f), new Vector2(8.5f, -2.6f), new Vector2(-8.5f, -2.6f) };
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

        static Hotspot AddHotspot(Transform parent, string displayName, Vector2 feet, Vector2 size, Color color,
            Vector2 standAt, bool faceLeft, string lookNode, string useNode, params (string item, string node)[] itemNodes)
        {
            // "Ms. Hush" -> ms_hush, "Sign-up sheet" -> sign_up_sheet: the name of its art file.
            var slug = System.Text.RegularExpressions.Regex.Replace(displayName.ToLowerInvariant(), "[^a-z0-9]+", "_").Trim('_');
            var go = new GameObject($"Hotspot_{slug}");
            go.transform.SetParent(parent, false);
            go.transform.position = feet;

            var sprite = go.AddComponent<SpriteRenderer>();
            sprite.sprite = Painted($"hs_{slug}", true) ??
                (roomIsPainted ? null : PlaceholderSprite($"hs_{slug}", Mathf.RoundToInt(size.x * 32), Mathf.RoundToInt(size.y * 32), color, 32, true));
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
            return hotspot;
        }

        // ---------- Boot scene ----------

        static void BuildSlotPrefab()
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

            PrefabUtility.SaveAsPrefabAsset(go, SlotPrefabPath);
            Object.DestroyImmediate(go);
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
            body.sprite = AssetDatabase.LoadAssetAtPath<Sprite>($"{PaintedFolder}/player_dex.png") ??
                AssetDatabase.LoadAssetAtPath<Sprite>($"{PlaceholderFolder}/player_dex.png");
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
            // Draw above Yarn's dialogue canvas so nothing covers the inventory.
            canvas.sortingOrder = 100;
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
            barRect.sizeDelta = new Vector2(0f, 96f);
            barRect.anchoredPosition = Vector2.zero;
            bar.AddComponent<Image>().color = new Color(0.08f, 0.05f, 0.1f, 0.7f);
            var layout = bar.AddComponent<HorizontalLayoutGroup>();
            layout.spacing = 10f;
            layout.padding = new RectOffset(16, 16, 12, 12);
            layout.childAlignment = TextAnchor.MiddleLeft;
            layout.childControlWidth = false;
            layout.childControlHeight = false;
            layout.childForceExpandWidth = false;
            layout.childForceExpandHeight = false;
            var barLabel = AddText(bar.transform, "Label", "POCKETS", 30f);
            ((RectTransform)barLabel.transform).sizeDelta = new Vector2(170f, 72f);
            barLabel.color = new Color(1f, 0.82f, 0.35f);
            barLabel.fontStyle = FontStyles.Bold;
            barLabel.raycastTarget = false;
            var emptyHint = AddText(bar.transform, "EmptyHint", "(empty: look around for stuff)", 26f);
            ((RectTransform)emptyHint.transform).sizeDelta = new Vector2(520f, 72f);
            emptyHint.alignment = TextAlignmentOptions.Left;
            emptyHint.color = new Color(1f, 1f, 1f, 0.6f);
            emptyHint.raycastTarget = false;

            var pickup = AddText(canvasGo.transform, "PickupText", "", 40f);
            var pickupRect = (RectTransform)pickup.transform;
            pickupRect.anchorMin = pickupRect.anchorMax = new Vector2(0.5f, 1f);
            pickupRect.pivot = new Vector2(0.5f, 1f);
            pickupRect.anchoredPosition = new Vector2(0f, -110f);
            pickupRect.sizeDelta = new Vector2(1000f, 60f);
            pickup.color = new Color(1f, 0.9f, 0.4f);
            pickup.fontStyle = FontStyles.Bold;
            pickup.raycastTarget = false;

            var inventory = bar.AddComponent<InventoryBar>();
            Set(inventory, "database", database);
            Set(inventory, "slotPrefab", slotPrefab);
            Set(inventory, "slotParent", bar.transform);
            Set(inventory, "emptyHint", emptyHint.gameObject);
            Set(inventory, "pickupText", pickup);

            // The held item follows the mouse. Last child of the bar's canvas so it draws on top,
            // and not a raycast target so drops land on whatever is underneath it.
            var heldGo = new GameObject("HeldItemCursor", typeof(RectTransform));
            heldGo.transform.SetParent(canvasGo.transform, false);
            ((RectTransform)heldGo.transform).sizeDelta = new Vector2(80f, 80f);
            var heldImage = heldGo.AddComponent<Image>();
            heldImage.raycastTarget = false;
            heldImage.preserveAspect = true;
            heldImage.enabled = false;
            Set(heldGo.AddComponent<HeldItemCursor>(), "image", heldImage);

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

        /// <summary>The finished-art sprite with this name, set up for import, or null if there isn't one yet.</summary>
        static Sprite Painted(string name, bool pivotAtFeet)
        {
            var path = $"{PaintedFolder}/{name}.png";
            if (!File.Exists(path)) return null;
            AssetDatabase.ImportAsset(path);
            var importer = (TextureImporter)AssetImporter.GetAtPath(path);
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.spritePixelsPerUnit = 100f;
            importer.filterMode = FilterMode.Bilinear;
            importer.mipmapEnabled = false;
            importer.alphaIsTransparency = true;
            importer.maxTextureSize = 2048;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            var settings = new TextureImporterSettings();
            importer.ReadTextureSettings(settings);
            settings.spriteAlignment = (int)(pivotAtFeet ? SpriteAlignment.BottomCenter : SpriteAlignment.Center);
            importer.SetTextureSettings(settings);
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Sprite>(path);
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
            // A file that no longer loads as T (for example after its script went missing) would
            // leave every reference to it empty, so replace it.
            if (File.Exists(path))
            {
                Debug.LogWarning($"Replacing {path}, which no longer loads as a {typeof(T).Name}.");
                AssetDatabase.DeleteAsset(path);
            }
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
