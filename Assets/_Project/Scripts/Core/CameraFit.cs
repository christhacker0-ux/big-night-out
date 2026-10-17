using UnityEngine;

namespace BigNightOut.Core
{
    /// <summary>
    /// Keeps the whole 19.2 x 10.8 room on screen at any window shape.
    /// On screens narrower than 16:9 (such as 16:10 laptops) the camera zooms out
    /// and shows black bars instead of cutting off exits at the room edges.
    /// Added to the main camera automatically, so no scene rebuild is needed.
    /// </summary>
    [RequireComponent(typeof(Camera))]
    public class CameraFit : MonoBehaviour
    {
        const float RoomHalfWidth = 9.6f;
        const float RoomHalfHeight = 5.4f;

        Camera cam;
        float lastAspect = -1f;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Attach()
        {
            var main = Camera.main;
            if (main != null && main.GetComponent<CameraFit>() == null)
                main.gameObject.AddComponent<CameraFit>();
        }

        void Awake() => cam = GetComponent<Camera>();

        void LateUpdate()
        {
            if (Mathf.Approximately(cam.aspect, lastAspect)) return;
            lastAspect = cam.aspect;
            cam.orthographicSize = Mathf.Max(RoomHalfHeight, RoomHalfWidth / cam.aspect);
        }
    }
}
