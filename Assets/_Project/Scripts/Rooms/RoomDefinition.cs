using UnityEngine;

namespace BigNightOut.Rooms
{
    [CreateAssetMenu(menuName = "Big Night Out/Room", fileName = "Room_")]
    public class RoomDefinition : ScriptableObject
    {
        [Tooltip("Stable id used in saves and Yarn, e.g. dorm_hallway.")]
        [SerializeField] string id;
        [Tooltip("Scene name as listed in Build Profiles.")]
        [SerializeField] string sceneName;
        [SerializeField] AudioClip music;

        public string Id => id;
        public string SceneName => sceneName;
        public AudioClip Music => music;
    }
}
