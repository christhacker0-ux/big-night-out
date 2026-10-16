using System.Collections;
using System.Collections.Generic;
using BigNightOut.Core;
using BigNightOut.Interaction;
using BigNightOut.Save;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace BigNightOut.Rooms
{
    /// <summary>
    /// Loads one room scene at a time on top of the Boot scene and places the player.
    /// Autosaves after each room change.
    /// </summary>
    public class RoomLoader : MonoBehaviour
    {
        [SerializeField] List<RoomDefinition> rooms = new List<RoomDefinition>();
        [SerializeField] PlayerMover player;

        string loadedScene;
        bool busy;

        public Room CurrentRoom { get; private set; }
        public RoomDefinition Find(string roomId) => rooms.Find(r => r != null && r.Id == roomId);
        public RoomDefinition AnyRoom => rooms.Count > 0 ? rooms[0] : null;

        void Awake()
        {
            rooms.RemoveAll(r => r == null);
            // A Boot scene whose room list was lost still plays: pick up every room in Resources/Rooms.
            if (rooms.Count == 0)
            {
                rooms.AddRange(Resources.LoadAll<RoomDefinition>("Rooms"));
                Debug.LogWarning($"The Room Loader's room list was empty, so it loaded {rooms.Count} room(s) from Resources/Rooms. Run Big Night Out > Build Dorm Hallway Slice to fix the Boot scene.");
            }
        }

        public void GoTo(string roomId, string entryName)
        {
            if (busy)
            {
                Debug.LogWarning($"Ignoring a move to '{roomId}' while another room is still loading.");
                return;
            }
            var room = Find(roomId);
            if (room == null)
            {
                Debug.LogError($"Unknown room id '{roomId}'. Add its RoomDefinition to the RoomLoader list.");
                return;
            }
            StartCoroutine(Load(room, entryName));
        }

        IEnumerator Load(RoomDefinition room, string entryName)
        {
            busy = true;

            if (!string.IsNullOrEmpty(loadedScene))
                yield return SceneManager.UnloadSceneAsync(loadedScene);

            var loading = LoadAdditive(room.SceneName);
            if (loading == null)
            {
                Debug.LogError($"Could not load the scene '{room.SceneName}' for room '{room.Id}'. Check that the scene exists and is in the build's scene list.");
                busy = false;
                yield break;
            }
            yield return loading;
            loadedScene = room.SceneName;
            SceneManager.SetActiveScene(SceneManager.GetSceneByName(room.SceneName));

            CurrentRoom = FindFirstObjectByType<Room>();
            if (CurrentRoom == null) Debug.LogError($"The scene '{room.SceneName}' has no Room component.");
            var entry = CurrentRoom != null ? CurrentRoom.FindEntry(entryName) : null;
            if (entry != null && player != null) player.Teleport(entry.transform.position, entry.FaceLeft);

            var state = GameState.Current;
            state.CurrentRoom = room.Id;
            state.CurrentEntry = entryName;
            SaveSystem.Autosave();

            busy = false;
            if (CurrentRoom != null) CurrentRoom.OnEntered();
        }

        // In the editor, load by asset path so rooms work even when they are missing from the build's scene list.
        static AsyncOperation LoadAdditive(string sceneName)
        {
#if UNITY_EDITOR
            foreach (var guid in UnityEditor.AssetDatabase.FindAssets($"{sceneName} t:Scene"))
            {
                var path = UnityEditor.AssetDatabase.GUIDToAssetPath(guid);
                if (System.IO.Path.GetFileNameWithoutExtension(path) == sceneName)
                    return UnityEditor.SceneManagement.EditorSceneManager.LoadSceneAsyncInPlayMode(path, new LoadSceneParameters(LoadSceneMode.Additive));
            }
#endif
            return SceneManager.LoadSceneAsync(sceneName, LoadSceneMode.Additive);
        }
    }
}
