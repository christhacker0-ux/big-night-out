using System;
using System.Collections.Generic;

namespace BigNightOut.Core
{
    /// <summary>
    /// The only state that is saved. Flags, counters, inventory, current room and act.
    /// Yarn commands are the only thing that should write to it during play.
    /// </summary>
    public class GameState
    {
        public static GameState Current { get; private set; } = new GameState();

        /// <summary>Raised after any change, including loading a save.</summary>
        public static event Action Changed;

        readonly Dictionary<string, bool> flags = new Dictionary<string, bool>();
        readonly Dictionary<string, int> counters = new Dictionary<string, int>();
        readonly List<string> inventory = new List<string>();

        public string CurrentRoom { get; set; } = "";
        public string CurrentEntry { get; set; } = "";
        public int Act { get; set; } = 1;

        public IReadOnlyList<string> Inventory => inventory;

        public bool GetFlag(string key) => flags.TryGetValue(key, out var value) && value;

        public void SetFlag(string key, bool value = true)
        {
            flags[key] = value;
            Changed?.Invoke();
        }

        public int GetCounter(string key) => counters.TryGetValue(key, out var value) ? value : 0;

        public void AddToCounter(string key, int amount)
        {
            counters[key] = GetCounter(key) + amount;
            Changed?.Invoke();
        }

        public bool HasItem(string itemId) => inventory.Contains(itemId);

        public void GiveItem(string itemId)
        {
            if (inventory.Contains(itemId)) return;
            inventory.Add(itemId);
            Changed?.Invoke();
        }

        public void TakeItem(string itemId)
        {
            if (inventory.Remove(itemId)) Changed?.Invoke();
        }

        public static void Reset()
        {
            Current = new GameState();
            Changed?.Invoke();
        }

        public SaveData ToSaveData()
        {
            var data = new SaveData
            {
                version = SaveData.CurrentVersion,
                room = CurrentRoom,
                entry = CurrentEntry,
                act = Act,
                inventory = new List<string>(inventory),
            };
            foreach (var pair in flags) data.flags.Add(new FlagEntry { key = pair.Key, value = pair.Value });
            foreach (var pair in counters) data.counters.Add(new CounterEntry { key = pair.Key, value = pair.Value });
            return data;
        }

        public static void Load(SaveData data)
        {
            var state = new GameState
            {
                CurrentRoom = data.room,
                CurrentEntry = data.entry,
                Act = data.act,
            };
            state.inventory.AddRange(data.inventory);
            foreach (var entry in data.flags) state.flags[entry.key] = entry.value;
            foreach (var entry in data.counters) state.counters[entry.key] = entry.value;
            Current = state;
            Changed?.Invoke();
        }
    }

    /// <summary>JsonUtility cannot serialise dictionaries, so saves use flat lists.</summary>
    [Serializable]
    public class SaveData
    {
        public const int CurrentVersion = 1;

        public int version;
        public string room;
        public string entry;
        public int act;
        public List<string> inventory = new List<string>();
        public List<FlagEntry> flags = new List<FlagEntry>();
        public List<CounterEntry> counters = new List<CounterEntry>();
    }

    [Serializable] public struct FlagEntry { public string key; public bool value; }
    [Serializable] public struct CounterEntry { public string key; public int value; }
}
