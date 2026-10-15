using BigNightOut.Core;
using UnityEngine;
using Yarn.Unity;

namespace BigNightOut.YarnBridge
{
    /// <summary>
    /// Put this next to the DialogueRunner in the Boot scene.
    /// It lets hotspots and items start Yarn nodes through DialogueService.
    /// </summary>
    [RequireComponent(typeof(DialogueRunner))]
    public class YarnDialogueStarter : MonoBehaviour, IDialogueStarter
    {
        DialogueRunner runner;

        void Awake()
        {
            runner = GetComponent<DialogueRunner>();
            DialogueService.Starter = this;
        }

        void OnDestroy()
        {
            if (ReferenceEquals(DialogueService.Starter, this)) DialogueService.Starter = null;
        }

        public bool IsRunning => runner != null && runner.IsDialogueRunning;

        public void Run(string nodeName)
        {
            if (IsRunning) return;
            _ = runner.StartDialogue(nodeName);
        }
    }
}
