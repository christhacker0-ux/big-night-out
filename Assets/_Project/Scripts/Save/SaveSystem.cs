using System.IO;
using BigNightOut.Core;
using UnityEngine;

namespace BigNightOut.Save
{
    /// <summary>
    /// Writes GameState to JSON files in Application.persistentDataPath/saves.
    /// Slot 0 is the autosave, written on every room change.
    /// </summary>
    public static class SaveSystem
    {
        public const int AutosaveSlot = 0;

        static string Folder => Path.Combine(Application.persistentDataPath, "saves");
        static string PathFor(int slot) => Path.Combine(Folder, $"slot_{slot}.json");

        public static void Autosave() => Save(AutosaveSlot);

        public static void Save(int slot)
        {
            Directory.CreateDirectory(Folder);
            var json = JsonUtility.ToJson(GameState.Current.ToSaveData(), true);
            File.WriteAllText(PathFor(slot), json);
        }

        public static bool Exists(int slot) => File.Exists(PathFor(slot));

        /// <summary>Loads the slot and sends the player to the saved room.</summary>
        public static bool Load(int slot)
        {
            if (!Exists(slot)) return false;
            var data = JsonUtility.FromJson<SaveData>(File.ReadAllText(PathFor(slot)));
            data = Migrate(data);
            GameState.Load(data);
            GameManager.Instance.Rooms.GoTo(data.room, data.entry);
            return true;
        }

        /// <summary>Upgrade old save files here when SaveData changes.</summary>
        static SaveData Migrate(SaveData data)
        {
            data.version = SaveData.CurrentVersion;
            return data;
        }
    }
}
