using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace BigNightOut.Inventory
{
    /// <summary>
    /// One icon in the inventory bar. Click to pick the item up, right click to look at it,
    /// or drag it onto a person, an object or another item to use it there.
    /// </summary>
    public class InventorySlot : MonoBehaviour, IPointerClickHandler, IBeginDragHandler, IDragHandler, IEndDragHandler
    {
        [SerializeField] Image icon;
        [SerializeField] GameObject heldHighlight;

        ItemDefinition item;
        InventoryBar bar;

        public ItemDefinition Item => item;

        public void Bind(ItemDefinition definition, InventoryBar owner, bool isHeld)
        {
            item = definition;
            bar = owner;
            if (icon == null)
            {
                var child = transform.Find("Icon");
                if (child != null) icon = child.GetComponent<Image>();
            }
            if (icon != null) icon.sprite = definition.Icon;
            SetHeld(isHeld);
        }

        public void SetHeld(bool isHeld)
        {
            if (heldHighlight != null) heldHighlight.SetActive(isHeld);
        }

        public void OnPointerClick(PointerEventData eventData)
        {
            if (eventData.button == PointerEventData.InputButton.Right) bar.RightClicked(item);
            else if (eventData.button == PointerEventData.InputButton.Left) bar.LeftClicked(item);
        }

        public void OnBeginDrag(PointerEventData eventData)
        {
            if (eventData.button != PointerEventData.InputButton.Left) return;
            InventorySelection.Hold(item);
        }

        // Needed so Unity sends begin and end drag; the held-item cursor does the drawing.
        public void OnDrag(PointerEventData eventData) { }

        public void OnEndDrag(PointerEventData eventData)
        {
            if (eventData.button != PointerEventData.InputButton.Left) return;
            var target = eventData.pointerCurrentRaycast.gameObject;
            if (target != null)
            {
                // Dropped on the UI: another item combines, anything else puts it back.
                var other = target.GetComponentInParent<InventorySlot>();
                InventorySelection.Clear();
                if (other != null && other != this) bar.Combine(item, other.item);
                return;
            }
            InventorySelection.DropInWorld(item, eventData.position);
        }
    }
}
