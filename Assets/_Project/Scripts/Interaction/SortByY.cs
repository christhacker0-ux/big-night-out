using UnityEngine;

namespace BigNightOut.Interaction
{
    /// <summary>Draws lower things in front, so the player can walk behind and in front of props.</summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class SortByY : MonoBehaviour
    {
        [Tooltip("Leave on for things that move, off for props that never do.")]
        [SerializeField] bool everyFrame = true;
        [SerializeField] int offset;

        SpriteRenderer sprite;

        void Awake()
        {
            sprite = GetComponent<SpriteRenderer>();
            Apply();
        }

        void LateUpdate()
        {
            if (everyFrame) Apply();
        }

        void Apply() => sprite.sortingOrder = offset - Mathf.RoundToInt(transform.position.y * 100f);
    }
}
