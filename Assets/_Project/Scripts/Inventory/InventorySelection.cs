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
            HeldChanged?.Invoke();
        }

        public static void Clear() => Hold(null);
    }
}
