using BigNightOut.Inventory;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UI;

namespace BigNightOut.UI
{
    /// <summary>Draws the held inventory item next to the mouse, while dragging or after picking it up.</summary>
    public class HeldItemCursor : MonoBehaviour
    {
        [SerializeField] Image image;
        [SerializeField] Vector2 offset = new Vector2(28f, -28f);

        void OnEnable()
        {
            InventorySelection.HeldChanged += Refresh;
            Refresh();
        }

        void OnDisable() => InventorySelection.HeldChanged -= Refresh;

        void Refresh()
        {
            var held = InventorySelection.Held;
            image.enabled = held != null && held.Icon != null;
            if (held != null) image.sprite = held.Icon;
        }

        void LateUpdate()
        {
            if (Mouse.current == null) return;
            var held = InventorySelection.Held;
            image.enabled = held != null && held.Icon != null && !InventorySelection.Dragging;
            if (!image.enabled) return;
            image.rectTransform.position = Mouse.current.position.ReadValue() + offset;
        }
    }
}
