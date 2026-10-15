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
            if (firstRoom != null) roomLoader.GoTo(firstRoom.Id, firstEntry);
        }
    }
}
