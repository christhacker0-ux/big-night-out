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

        public void GoTo(string roomId, string entryName)
        {
            if (busy) return;
            var room = rooms.Find(r => r.Id == roomId);
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

            yield return SceneManager.LoadSceneAsync(room.SceneName, LoadSceneMode.Additive);
            loadedScene = room.SceneName;
            SceneManager.SetActiveScene(SceneManager.GetSceneByName(room.SceneName));

            CurrentRoom = FindFirstObjectByType<Room>();
            var entry = CurrentRoom != null ? CurrentRoom.FindEntry(entryName) : null;
            if (entry != null && player != null) player.Teleport(entry.transform.position, entry.FaceLeft);

            var state = GameState.Current;
            state.CurrentRoom = room.Id;
            state.CurrentEntry = entryName;
            SaveSystem.Autosave();

            busy = false;
            if (CurrentRoom != null) CurrentRoom.OnEntered();
        }
    }
}
