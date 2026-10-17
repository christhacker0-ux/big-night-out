using System;

namespace BigNightOut.Inventory
{
    /// <summary>The item the player is currently holding on the cursor, if any.</summary>
    public static class InventorySelection
    {
        public static ItemDefinition Held { get; private set; }

        /// <summary>True while an item is being dragged out of the bar; the slot draws its own icon then.</summary>
        public static bool Dragging { get; set; }

        public static event Action HeldChanged;

        public static void Hold(ItemDefinition item)
        {
            Held = item;
            if (HeldChanged == null) return;
            foreach (var listener in HeldChanged.GetInvocationList())
            {
                try { ((Action)listener)(); }
                catch (Exception e) { UnityEngine.Debug.LogException(e); }
            }
        }

        public static void Clear() => Hold(null);

        /// <summary>Raised when an item is dragged out of the inventory and let go over the room.</summary>
        public static event Action<ItemDefinition, UnityEngine.Vector2> DroppedInWorld;

        public static void DropInWorld(ItemDefinition item, UnityEngine.Vector2 screenPosition)
        {
            if (DroppedInWorld == null) { Clear(); return; }
            try { DroppedInWorld(item, screenPosition); }
            catch (Exception e) { UnityEngine.Debug.LogException(e); Clear(); }
        }
    }
}
