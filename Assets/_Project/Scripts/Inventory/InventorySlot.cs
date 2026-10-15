using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace BigNightOut.Inventory
{
    /// <summary>One icon in the inventory bar. Put it on a UI Image.</summary>
    public class InventorySlot : MonoBehaviour, IPointerClickHandler
    {
        [SerializeField] Image icon;
        [SerializeField] GameObject heldHighlight;

        ItemDefinition item;
        InventoryBar bar;

        public void Bind(ItemDefinition definition, InventoryBar owner, bool isHeld)
        {
            item = definition;
            bar = owner;
            icon.sprite = definition.Icon;
            if (heldHighlight != null) heldHighlight.SetActive(isHeld);
        }

        public void OnPointerClick(PointerEventData eventData)
        {
            if (eventData.button == PointerEventData.InputButton.Right) bar.RightClicked(item);
            else if (eventData.button == PointerEventData.InputButton.Left) bar.LeftClicked(item);
        }
    }
}
