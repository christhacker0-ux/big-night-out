using System.Collections.Generic;
using BigNightOut.Core;
using UnityEngine;

namespace BigNightOut.Inventory
{
    /// <summary>
    /// Builds one InventorySlot per item the player has. Left click holds an item,
    /// or combines it with the held one; right click looks at it.
    /// </summary>
    public class InventoryBar : MonoBehaviour
    {
        [SerializeField] ItemDatabase database;
        [SerializeField] InventorySlot slotPrefab;
        [SerializeField] Transform slotParent;

        readonly List<InventorySlot> slots = new List<InventorySlot>();

        void Awake() => ItemDatabase.Active = database;

        void OnEnable()
        {
            GameState.Changed += Rebuild;
            InventorySelection.HeldChanged += Rebuild;
            Rebuild();
        }

        void OnDisable()
        {
            GameState.Changed -= Rebuild;
            InventorySelection.HeldChanged -= Rebuild;
        }

        void Rebuild()
        {
            foreach (var slot in slots) Destroy(slot.gameObject);
            slots.Clear();

            foreach (var id in GameState.Current.Inventory)
            {
                var item = database.Find(id);
                if (item == null)
                {
                    Debug.LogWarning($"Item '{id}' is in the inventory but not in the ItemDatabase.");
                    continue;
                }
                var slot = Instantiate(slotPrefab, slotParent);
                slot.Bind(item, this, InventorySelection.Held == item);
                slots.Add(slot);
            }
        }

        public void LeftClicked(ItemDefinition item)
        {
            var held = InventorySelection.Held;
            if (held == null)
            {
                InventorySelection.Hold(item);
                return;
            }
            InventorySelection.Clear();
            if (held != item) DialogueService.Run(database.CombineNode(held.Id, item.Id));
        }

        public void RightClicked(ItemDefinition item)
        {
            InventorySelection.Clear();
            DialogueService.Run(item.LookNode);
        }
    }
}
