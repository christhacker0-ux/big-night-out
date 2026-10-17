using System.Collections.Generic;
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
        RectTransform ghost;
        static readonly List<RaycastResult> hits = new List<RaycastResult>();

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
            InventorySelection.Dragging = true;
            InventorySelection.Hold(item);
            MakeGhost(eventData.position);
            if (icon != null) icon.color = new Color(1f, 1f, 1f, 0.35f);
        }

        public void OnDrag(PointerEventData eventData)
        {
            if (ghost != null) ghost.position = eventData.position;
        }

        public void OnEndDrag(PointerEventData eventData)
        {
            if (eventData.button != PointerEventData.InputButton.Left) return;
            EndDragVisuals();

            // Let go over another pocket item: combine. Over the pockets bar: put it back.
            // Anywhere else counts as the room, even if some other UI happens to be on top.
            var over = UiUnder(eventData);
            if (over != null)
            {
                InventorySelection.Clear();
                var other = over.GetComponentInParent<InventorySlot>();
                if (other != null && other != this) bar.Combine(item, other.item);
                return;
            }
            InventorySelection.DropInWorld(item, eventData.position);
        }

        void OnDisable()
        {
            // The bar can rebuild mid-drag (a pickup, a dialogue give); never leave a ghost behind.
            if (ghost != null) EndDragVisuals();
        }

        GameObject UiUnder(PointerEventData eventData)
        {
            if (EventSystem.current == null) return null;
            hits.Clear();
            EventSystem.current.RaycastAll(eventData, hits);
            foreach (var hit in hits)
            {
                if (hit.gameObject == null) continue;
                if (hit.gameObject.GetComponentInParent<InventorySlot>() != null) return hit.gameObject;
                if (hit.gameObject.GetComponentInParent<InventoryBar>() != null) return hit.gameObject;
            }
            return null;
        }

        void MakeGhost(Vector2 screen)
        {
            var canvas = GetComponentInParent<Canvas>();
            if (canvas == null || item == null || item.Icon == null) return;
            var go = new GameObject("DraggedItem", typeof(RectTransform));
            ghost = (RectTransform)go.transform;
            ghost.SetParent(canvas.rootCanvas.transform, false);
            ghost.SetAsLastSibling();
            ghost.sizeDelta = new Vector2(96f, 96f);
            var image = go.AddComponent<Image>();
            image.sprite = item.Icon;
            image.preserveAspect = true;
            image.raycastTarget = false;
            ghost.position = screen;
        }

        void EndDragVisuals()
        {
            InventorySelection.Dragging = false;
            if (ghost != null) Destroy(ghost.gameObject);
            ghost = null;
            if (icon != null) icon.color = Color.white;
        }
    }
}
