using TMPro;
using UnityEngine;

namespace BigNightOut.UI
{
    /// <summary>The name of whatever is under the cursor, drawn just above it.</summary>
    public class HoverLabel : MonoBehaviour
    {
        [SerializeField] TMP_Text label;
        [SerializeField] RectTransform root;
        [SerializeField] Vector2 offset = new Vector2(0f, 40f);

        public void Show(string text, Vector2 screenPosition)
        {
            if (!root.gameObject.activeSelf) root.gameObject.SetActive(true);
            label.text = text;
            root.position = screenPosition + offset;
        }

        public void Hide()
        {
            if (root.gameObject.activeSelf) root.gameObject.SetActive(false);
        }
    }
}
