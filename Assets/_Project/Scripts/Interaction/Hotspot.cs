using System;
using System.Collections.Generic;
using BigNightOut.Core;
using UnityEngine;

namespace BigNightOut.Interaction
{
    /// <summary>
    /// Anything the player can look at, use, talk to or use an item on.
    /// Every response is a Yarn node, so puzzle logic lives in .yarn files.
    /// Needs a Collider2D (set to Is Trigger) for mouse picking.
    /// </summary>
    [RequireComponent(typeof(Collider2D))]
    public class Hotspot : MonoBehaviour
    {
        [Serializable]
        public struct ItemResponse
        {
            public string itemId;
            public string node;
        }

        [Tooltip("Name shown on hover. Later this becomes a localisation key.")]
        [SerializeField] string displayName = "Thing";
        [Tooltip("Where the player stands to interact. Empty = no walking.")]
        [SerializeField] Transform walkTo;
        [SerializeField] bool faceLeftOnArrival;

        [Header("Yarn nodes")]
        [SerializeField] string lookNode;
        [Tooltip("Left click: use, talk, or pick up.")]
        [SerializeField] string useNode;
        [SerializeField] List<ItemResponse> itemNodes = new List<ItemResponse>();
        [Tooltip("Runs when an item with no specific response is used here.")]
        [SerializeField] string wrongItemNode = "Generic_WrongItem";

        [Header("Visibility")]
        [Tooltip("Hide this hotspot while this flag is set, e.g. once an item is picked up.")]
        [SerializeField] string hideWhenFlag;

        public string DisplayName => displayName;
        public Transform WalkTo => walkTo;
        public bool FaceLeftOnArrival => faceLeftOnArrival;

        void OnEnable()
        {
            GameState.Changed += Refresh;
            Refresh();
        }

        void OnDisable() => GameState.Changed -= Refresh;

        void Refresh()
        {
            if (string.IsNullOrEmpty(hideWhenFlag)) return;
            var hidden = GameState.Current.GetFlag(hideWhenFlag);
            foreach (var r in GetComponentsInChildren<Renderer>()) r.enabled = !hidden;
            foreach (var c in GetComponents<Collider2D>()) c.enabled = !hidden;
        }

        public void Look() => DialogueService.Run(lookNode);

        public void Use() => DialogueService.Run(useNode);

        public void UseItem(string itemId)
        {
            foreach (var response in itemNodes)
            {
                if (response.itemId == itemId)
                {
                    DialogueService.Run(response.node);
                    return;
                }
            }
            DialogueService.Run(wrongItemNode);
        }
    }
}
