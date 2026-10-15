using System;
using UnityEngine;

namespace BigNightOut.Interaction
{
    /// <summary>
    /// Walks the player to a point on the current WalkableArea.
    /// Moves in a straight line for now; swap in pathfinding (A* over the polygon,
    /// or NavMeshPlus) once rooms have obstacles in the middle of the floor.
    /// </summary>
    public class PlayerMover : MonoBehaviour
    {
        [SerializeField] float speed = 3.5f;
        [SerializeField] Animator animator;
        [SerializeField] Transform visual;

        static readonly int SpeedParam = Animator.StringToHash("Speed");

        Vector2? target;
        Action onArrived;

        public bool IsWalking => target.HasValue;

        public void WalkTo(Vector2 point, Action arrived = null)
        {
            var area = WalkableArea.Current;
            target = area != null ? area.Clamp(point) : point;
            onArrived = arrived;
        }

        public void Stop()
        {
            target = null;
            onArrived = null;
        }

        public void Teleport(Vector2 point, bool faceLeft)
        {
            Stop();
            transform.position = point;
            Face(faceLeft);
            ApplyDepthScale();
        }

        void Update()
        {
            if (!target.HasValue)
            {
                if (animator != null) animator.SetFloat(SpeedParam, 0f);
                return;
            }

            var position = (Vector2)transform.position;
            var next = Vector2.MoveTowards(position, target.Value, speed * Time.deltaTime);
            if (Mathf.Abs(next.x - position.x) > 0.001f) Face(next.x < position.x);
            transform.position = next;
            ApplyDepthScale();
            if (animator != null) animator.SetFloat(SpeedParam, speed);

            if ((next - target.Value).sqrMagnitude < 0.0001f)
            {
                var callback = onArrived;
                Stop();
                callback?.Invoke();
            }
        }

        void Face(bool left)
        {
            if (visual == null) return;
            var scale = visual.localScale;
            scale.x = Mathf.Abs(scale.x) * (left ? -1f : 1f);
            visual.localScale = scale;
        }

        void ApplyDepthScale()
        {
            var area = WalkableArea.Current;
            if (area == null) return;
            var s = area.ScaleAt(transform.position.y);
            transform.localScale = new Vector3(s, s, 1f);
        }
    }
}
