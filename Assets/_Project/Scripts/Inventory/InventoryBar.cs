using System.Collections;
using System.Collections.Generic;
using BigNightOut.Core;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

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
        [Tooltip("Shown while the inventory is empty.")]
        [SerializeField] GameObject emptyHint;
        [Tooltip("Briefly shows \"Got: <item>\" when something new arrives.")]
        [SerializeField] TMP_Text pickupText;

        readonly List<InventorySlot> slots = new List<InventorySlot>();
        readonly HashSet<string> known = new HashSet<string>();
        Coroutine pickupRoutine;
        bool firstRebuild = true;

        void Awake()
        {
            if (database == null) database = Resources.Load<ItemDatabase>("Items/ItemDatabase");
            if (database == null) Debug.LogError("No item database. Run Big Night Out > Build Dorm Hallway Slice.");
            ItemDatabase.Active = database;
            if (slotParent == null) slotParent = transform;
            if (pickupText != null) pickupText.text = "";
        }

        void OnEnable()
        {
            GameState.Changed += Rebuild;
            InventorySelection.HeldChanged += RefreshHeld;
            Rebuild();
        }

        void OnDisable()
        {
            GameState.Changed -= Rebuild;
            InventorySelection.HeldChanged -= RefreshHeld;
        }

        bool rebuilding;

        void Rebuild()
        {
            if (rebuilding) return;
            rebuilding = true;
            try { RebuildSlots(); }
            finally { rebuilding = false; }
        }

        void RebuildSlots()
        {
            Debug.Log($"[BNO] inventory rebuild: {string.Join(", ", GameState.Current.Inventory)}");
            foreach (var slot in slots) if (slot != null) Destroy(slot.gameObject);
            slots.Clear();
            var arrived = new List<ItemDefinition>();

            foreach (var id in GameState.Current.Inventory)
            {
                var item = database != null ? database.Find(id) : null;
                if (item == null)
                {
                    Debug.LogWarning($"Item '{id}' is in the inventory but not in the ItemDatabase.");
                    continue;
                }
                var slot = slotPrefab != null ? Instantiate(slotPrefab, slotParent) : MakeSlot();
                slot.Bind(item, this, InventorySelection.Held == item);
                slots.Add(slot);

                if (known.Add(id)) arrived.Add(item);
            }
            known.IntersectWith(GameState.Current.Inventory);
            // One new item is a pickup; several at once is a load or a new game, so say nothing.
            if (arrived.Count == 1 && !firstRebuild) ShowPickup(arrived[0]);
            firstRebuild = false;
            if (emptyHint != null) emptyHint.SetActive(slots.Count == 0);
            Debug.Log($"[BNO] inventory rebuilt with {slots.Count} slot(s)");
        }

        // Only the highlight changes when an item is picked up. Rebuilding here would destroy
        // the slot that is being dragged and cancel the drag.
        void RefreshHeld()
        {
            foreach (var slot in slots)
                if (slot != null) slot.SetHeld(slot.Item != null && slot.Item == InventorySelection.Held);
        }

        /// <summary>Used when the slot prefab reference is missing, so items still show.</summary>
        InventorySlot MakeSlot()
        {
            var go = new GameObject("InventorySlot", typeof(RectTransform));
            go.transform.SetParent(slotParent, false);
            ((RectTransform)go.transform).sizeDelta = new Vector2(72f, 72f);
            go.AddComponent<Image>().color = new Color(0f, 0f, 0f, 0.4f);
            var icon = new GameObject("Icon", typeof(RectTransform));
            icon.transform.SetParent(go.transform, false);
            var rect = (RectTransform)icon.transform;
            rect.anchorMin = Vector2.zero;
            rect.anchorMax = Vector2.one;
            rect.offsetMin = new Vector2(6f, 6f);
            rect.offsetMax = new Vector2(-6f, -6f);
            icon.AddComponent<Image>().raycastTarget = false;
            return go.AddComponent<InventorySlot>();
        }

        void ShowPickup(ItemDefinition item)
        {
            if (pickupText == null) return;
            if (pickupRoutine != null) StopCoroutine(pickupRoutine);
            pickupRoutine = StartCoroutine(Pickup(item.DisplayName));
        }

        IEnumerator Pickup(string itemName)
        {
            pickupText.text = $"Got: {itemName}";
            yield return new WaitForSecondsRealtime(2.5f);
            pickupText.text = "";
            pickupRoutine = null;
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
            if (held != item) Combine(held, item);
        }

        public void Combine(ItemDefinition a, ItemDefinition b)
        {
            if (database == null) return;
            DialogueService.Run(database.CombineNode(a.Id, b.Id));
        }

        public void RightClicked(ItemDefinition item)
        {
            InventorySelection.Clear();
            DialogueService.Run(item.LookNode);
        }
    }
}
