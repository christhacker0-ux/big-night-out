using System;
using System.Collections.Generic;
using UnityEngine;

namespace BigNightOut.Inventory
{
    /// <summary>
    /// Every item in the game, plus which item pairs combine and the Yarn node that handles it.
    /// Keep exactly one of these in the project and assign it to the InventoryBar.
    /// </summary>
    [CreateAssetMenu(menuName = "Big Night Out/Item Database", fileName = "ItemDatabase")]
    public class ItemDatabase : ScriptableObject
    {
        [Serializable]
        public struct Combination
        {
            public string itemA;
            public string itemB;
            public string node;
        }

        [SerializeField] List<ItemDefinition> items = new List<ItemDefinition>();
        [SerializeField] List<Combination> combinations = new List<Combination>();
        [SerializeField] string failedCombineNode = "Generic_CantCombine";

        public static ItemDatabase Active { get; set; }

        public ItemDefinition Find(string id)
        {
            var item = items.Find(i => i != null && i.Id == id);
            if (item != null) return item;
            // Fall back to Resources/Items in case the list lost its references.
            foreach (var candidate in Resources.LoadAll<ItemDefinition>("Items"))
                if (candidate.Id == id) return candidate;
            return null;
        }

        /// <summary>The Yarn node for combining two items, in either order.</summary>
        public string CombineNode(string a, string b)
        {
            foreach (var c in combinations)
                if ((c.itemA == a && c.itemB == b) || (c.itemA == b && c.itemB == a))
                    return c.node;
            return failedCombineNode;
        }
    }
}
