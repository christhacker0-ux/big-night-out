using UnityEngine;

namespace BigNightOut.Interaction
{
    /// <summary>
    /// The floor of a room, drawn as a PolygonCollider2D (set it to Is Trigger).
    /// Also scales characters by depth: smaller near the top of the area.
    /// </summary>
    [RequireComponent(typeof(PolygonCollider2D))]
    public class WalkableArea : MonoBehaviour
    {
        [Tooltip("Character scale from the bottom of the area (0) to the top (1).")]
        [SerializeField] AnimationCurve scaleByDepth = AnimationCurve.Linear(0f, 1f, 1f, 0.6f);

        PolygonCollider2D area;

        public static WalkableArea Current { get; private set; }

        void Awake() => area = GetComponent<PolygonCollider2D>();
        void OnEnable() => Current = this;
        void OnDisable() { if (Current == this) Current = null; }

        public bool Contains(Vector2 point) => area.OverlapPoint(point);

        /// <summary>The nearest point on the floor to where the player clicked.</summary>
        public Vector2 Clamp(Vector2 point) => Contains(point) ? point : area.ClosestPoint(point);

        public float ScaleAt(float y)
        {
            var bounds = area.bounds;
            var t = Mathf.InverseLerp(bounds.min.y, bounds.max.y, y);
            return scaleByDepth.Evaluate(t);
        }
    }
}
