using UnityEngine;

namespace BigNightOut.Rooms
{
    /// <summary>Where the player appears when entering a room, e.g. "from_stairs".</summary>
    public class EntryPoint : MonoBehaviour
    {
        [SerializeField] string entryName = "start";
        [SerializeField] bool faceLeft;

        public string EntryName => entryName;
        public bool FaceLeft => faceLeft;
    }
}
