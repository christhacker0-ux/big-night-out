using System;

namespace BigNightOut.Inventory
{
    /// <summary>The item the player is currently holding on the cursor, if any.</summary>
    public static class InventorySelection
    {
        public static ItemDefinition Held { get; private set; }

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
    }
}
