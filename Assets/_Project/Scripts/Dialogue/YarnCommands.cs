using BigNightOut.Core;
using UnityEngine;
using Yarn.Unity;

namespace BigNightOut.YarnBridge
{
    /// <summary>
    /// The Yarn commands and functions that read and change game state.
    /// Commands:  <<give earplugs>>  <<take earplugs>>  <<flag met_lacey>>  <<unflag met_lacey>>
    ///            <<add confidence 1>>  <<go dorm_hallway from_stairs>>  <<act 2>>
    /// Functions: has("earplugs")  flagged("met_lacey")  counter("confidence")  current_act()
    /// </summary>
    public static class YarnCommands
    {
        [YarnCommand("give")]
        public static void Give(string itemId)
        {
            Debug.Log($"[BNO] give {itemId}");
            GameState.Current.GiveItem(itemId);
            Debug.Log($"[BNO] gave {itemId}");
        }

        [YarnCommand("take")]
        public static void Take(string itemId) => GameState.Current.TakeItem(itemId);

        [YarnCommand("flag")]
        public static void Flag(string key) => GameState.Current.SetFlag(key, true);

        [YarnCommand("unflag")]
        public static void Unflag(string key) => GameState.Current.SetFlag(key, false);

        [YarnCommand("add")]
        public static void Add(string key, int amount) => GameState.Current.AddToCounter(key, amount);

        [YarnCommand("act")]
        public static void SetAct(int act) => GameState.Current.Act = act;

        [YarnCommand("go")]
        public static void Go(string roomId, string entryName) => GameManager.Instance.Rooms.GoTo(roomId, entryName);

        [YarnFunction("has")]
        public static bool Has(string itemId) => GameState.Current.HasItem(itemId);

        [YarnFunction("flagged")]
        public static bool IsFlagged(string key) => GameState.Current.GetFlag(key);

        [YarnFunction("counter")]
        public static int Counter(string key) => GameState.Current.GetCounter(key);

        [YarnFunction("current_act")]
        public static int CurrentAct() => GameState.Current.Act;
    }
}
