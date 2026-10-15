using UnityEngine;

namespace BigNightOut.Inventory
{
    [CreateAssetMenu(menuName = "Big Night Out/Item", fileName = "Item_")]
    public class ItemDefinition : ScriptableObject
    {
        [Tooltip("Stable id used in saves and Yarn, e.g. earplugs.")]
        [SerializeField] string id;
        [SerializeField] string displayName;
        [SerializeField] Sprite icon;
        [Tooltip("Yarn node run when the player right-clicks the item.")]
        [SerializeField] string lookNode;

        public string Id => id;
        public string DisplayName => displayName;
        public Sprite Icon => icon;
        public string LookNode => lookNode;
    }
}
