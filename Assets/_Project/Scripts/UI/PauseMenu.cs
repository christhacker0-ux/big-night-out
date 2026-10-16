using BigNightOut.Core;
using BigNightOut.Save;
using TMPro;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.UI;

namespace BigNightOut.UI
{
    /// <summary>
    /// Esc opens and closes the menu. One manual save slot for now (slot 1);
    /// slot 0 stays the autosave written on every room change.
    /// </summary>
    public class PauseMenu : MonoBehaviour
    {
        const int ManualSlot = 1;

        [SerializeField] GameObject panel;
        [SerializeField] Button resumeButton;
        [SerializeField] Button saveButton;
        [SerializeField] Button loadButton;
        [SerializeField] Button quitButton;
        [SerializeField] TMP_Text status;

        public bool IsOpen => panel != null && panel.activeSelf;

        void Awake()
        {
            resumeButton.onClick.AddListener(Close);
            saveButton.onClick.AddListener(SaveGame);
            loadButton.onClick.AddListener(LoadGame);
            quitButton.onClick.AddListener(Application.Quit);
            panel.SetActive(false);
        }

        void Update()
        {
            var keyboard = Keyboard.current;
            if (keyboard == null || !keyboard.escapeKey.wasPressedThisFrame) return;
            if (IsOpen) Close();
            else if (!DialogueService.IsRunning) Open();
        }

        public void Open()
        {
            panel.SetActive(true);
            loadButton.interactable = SaveSystem.Exists(ManualSlot);
            status.text = "";
            Time.timeScale = 0f;
        }

        public void Close()
        {
            panel.SetActive(false);
            Time.timeScale = 1f;
        }

        void SaveGame()
        {
            SaveSystem.Save(ManualSlot);
            loadButton.interactable = true;
            status.text = "Game saved.";
        }

        void LoadGame()
        {
            Close();
            if (!SaveSystem.Load(ManualSlot)) Open();
        }
    }
}
