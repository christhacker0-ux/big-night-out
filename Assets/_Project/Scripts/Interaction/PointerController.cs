using BigNightOut.Core;
using BigNightOut.Inventory;
using BigNightOut.UI;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;

namespace BigNightOut.Interaction
{
    /// <summary>
    /// The modern adventure control scheme:
    /// left click walks or uses, right click looks (or drops the held item),
    /// and a held inventory item is used on whatever is clicked next
    /// (or whatever it is dragged onto from the inventory bar).
    /// </summary>
    public class PointerController : MonoBehaviour
    {
        [SerializeField] Camera worldCamera;
        [SerializeField] PlayerMover player;
        [SerializeField] HoverLabel hoverLabel;

        bool wasTalking;

        void OnEnable() => InventorySelection.DroppedInWorld += DropItem;
        void OnDisable() => InventorySelection.DroppedInWorld -= DropItem;

        // An item dragged from the bar and let go over the room: use it on what is under it.
        void DropItem(ItemDefinition item, Vector2 screen)
        {
            var hotspot = DialogueService.IsRunning ? null : HotspotAt(worldCamera.ScreenToWorldPoint(screen));
            if (hotspot == null)
            {
                InventorySelection.Clear();
                return;
            }
            WalkThen(hotspot, () =>
            {
                InventorySelection.Clear();
                hotspot.UseItem(item.Id);
            });
        }

        void Update()
        {
            var mouse = Mouse.current;
            if (mouse == null) return;

            // Skip the frame a conversation ends too: the click that closed the last line
            // must not also start a new one while the dialogue system is still finishing.
            var talking = DialogueService.IsRunning;
            var justFinished = wasTalking && !talking;
            wasTalking = talking;
            if (talking || justFinished)
            {
                hoverLabel?.Hide();
                return;
            }

            if (EventSystem.current != null && EventSystem.current.IsPointerOverGameObject())
            {
                hoverLabel?.Hide();
                return;
            }

            var screen = mouse.position.ReadValue();
            var world = (Vector2)worldCamera.ScreenToWorldPoint(screen);
            var hotspot = HotspotAt(world);

            UpdateHover(hotspot, screen);

            if (mouse.leftButton.wasPressedThisFrame) LeftClick(hotspot, world);
            else if (mouse.rightButton.wasPressedThisFrame) RightClick(hotspot);
        }

        // The floor is a collider too, so look through everything under the cursor.
        static Hotspot HotspotAt(Vector2 world)
        {
            foreach (var hit in Physics2D.OverlapPointAll(world))
            {
                var hotspot = hit.GetComponentInParent<Hotspot>();
                if (hotspot != null) return hotspot;
            }
            return null;
        }

        void UpdateHover(Hotspot hotspot, Vector2 screen)
        {
            if (hoverLabel == null) return;
            var held = InventorySelection.Held;
            if (hotspot == null && held == null)
            {
                hoverLabel.Hide();
                return;
            }
            var text = held != null
                ? (hotspot != null ? $"Use {held.DisplayName} on {hotspot.DisplayName}" : $"Use {held.DisplayName} on...")
                : hotspot.DisplayName;
            hoverLabel.Show(text, screen);
        }

        void LeftClick(Hotspot hotspot, Vector2 world)
        {
            if (hotspot == null)
            {
                player.WalkTo(world);
                return;
            }

            var held = InventorySelection.Held;
            WalkThen(hotspot, () =>
            {
                if (held != null)
                {
                    InventorySelection.Clear();
                    hotspot.UseItem(held.Id);
                }
                else
                {
                    hotspot.Use();
                }
            });
        }

        void RightClick(Hotspot hotspot)
        {
            if (InventorySelection.Held != null)
            {
                InventorySelection.Clear();
                return;
            }
            if (hotspot != null) hotspot.Look();
        }

        void WalkThen(Hotspot hotspot, System.Action action)
        {
            if (hotspot.WalkTo == null)
            {
                player.Stop();
                action();
                return;
            }
            player.WalkTo(hotspot.WalkTo.position, () =>
            {
                player.Teleport(player.transform.position, hotspot.FaceLeftOnArrival);
                action();
            });
        }
    }
}
