using BigNightOut.Rooms;
using UnityEngine;

namespace BigNightOut.Core
{
    /// <summary>
    /// Lives in the Boot scene, which stays loaded for the whole game.
    /// Starts the first room on play.
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [SerializeField] RoomLoader roomLoader;
        [SerializeField] RoomDefinition firstRoom;
        [SerializeField] string firstEntry = "start";
        [Tooltip("Used when First Room is empty.")]
        [SerializeField] string fallbackFirstRoomId = "dex_room";

        public RoomLoader Rooms => roomLoader;

        void Awake()
        {
            if (Instance != null)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
        }

        void Start()
        {
            if (roomLoader == null)
            {
                Debug.LogError("GameManager has no Room Loader. Run Big Night Out > Build Dorm Hallway Slice to rebuild the Boot scene.");
                return;
            }
            var room = firstRoom != null ? firstRoom : roomLoader.Find(fallbackFirstRoomId) ?? roomLoader.AnyRoom;
            if (room == null)
            {
                Debug.LogError("No first room is set and the Room Loader has no rooms. Run Big Night Out > Build Dorm Hallway Slice to rebuild the Boot scene.");
                return;
            }
            Debug.Log($"Big Night Out: starting in room '{room.Id}'.");
            roomLoader.GoTo(room.Id, firstEntry);
        }
    }
}
