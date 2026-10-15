using BigNightOut.Core;
using UnityEngine;

namespace BigNightOut.Rooms
{
    /// <summary>
    /// One per room scene. Knows its entry points and an optional Yarn node
    /// that runs every time the player enters (for room-specific setup).
    /// </summary>
    public class Room : MonoBehaviour
    {
        [SerializeField] RoomDefinition definition;
        [SerializeField] string onEnterNode;

        public RoomDefinition Definition => definition;

        public EntryPoint FindEntry(string entryName)
        {
            foreach (var entry in GetComponentsInChildren<EntryPoint>())
                if (entry.EntryName == entryName) return entry;
            Debug.LogWarning($"Room '{name}' has no entry '{entryName}', using the first one.");
            return GetComponentInChildren<EntryPoint>();
        }

        public void OnEntered() => DialogueService.Run(onEnterNode);
    }
}
