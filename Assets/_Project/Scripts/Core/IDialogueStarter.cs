namespace BigNightOut.Core
{
    /// <summary>
    /// Lets core code start a dialogue node without depending on Yarn Spinner.
    /// The Yarn bridge registers itself here when the Yarn package is installed.
    /// </summary>
    public interface IDialogueStarter
    {
        bool IsRunning { get; }
        void Run(string nodeName);
    }

    public static class DialogueService
    {
        public static IDialogueStarter Starter { get; set; }

        public static bool IsRunning => Starter != null && Starter.IsRunning;

        public static void Run(string nodeName)
        {
            if (string.IsNullOrEmpty(nodeName)) return;
            if (Starter == null)
            {
                UnityEngine.Debug.LogWarning($"No dialogue system registered; wanted node '{nodeName}'. Is Yarn Spinner installed?");
                return;
            }
            Starter.Run(nodeName);
        }
    }
}
