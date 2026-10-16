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

        bool starting;

        public bool IsRunning => starting || (runner != null && runner.IsDialogueRunning);

        // Start on the next frame, so a dialogue never starts inside the same input event
        // or the same frame in which the previous one is still shutting down.
        public void Run(string nodeName)
        {
            if (IsRunning) return;
            StartCoroutine(StartNextFrame(nodeName));
        }

        System.Collections.IEnumerator StartNextFrame(string nodeName)
        {
            starting = true;
            yield return null;
            starting = false;
            if (runner.IsDialogueRunning) yield break;
            _ = runner.StartDialogue(nodeName);
        }
    }
}
