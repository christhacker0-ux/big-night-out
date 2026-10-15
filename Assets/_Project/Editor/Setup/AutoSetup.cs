using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using UnityEngine;

namespace BigNightOut.EditorTools
{
    /// <summary>
    /// Runs every time the editor loads scripts. On a fresh checkout it installs the packages
    /// the game needs (Input System, UGUI, Yarn Spinner), waits for them to compile, then builds
    /// the dorm hallway slice once. After the Boot scene exists it does nothing.
    /// Lives in its own assembly with no references, so it still runs while the game code
    /// cannot compile yet.
    /// </summary>
    [InitializeOnLoad]
    static class AutoSetup
    {
        const string YarnGitUrl = "https://github.com/YarnSpinnerTool/YarnSpinner-Unity.git#current";
        const string BootScene = "Assets/_Project/Scenes/Boot.unity";
        const string ManifestPath = "Packages/manifest.json";
        const string TriedInstallKey = "BigNightOut.AutoSetup.TriedInstall";

        static AddAndRemoveRequest request;

        static AutoSetup() => EditorApplication.delayCall += Run;

        [MenuItem("Big Night Out/Run First-Time Setup Again")]
        static void RunAgain()
        {
            SessionState.SetBool(TriedInstallKey, false);
            Run();
        }

        static void Run()
        {
            if (File.Exists(BootScene) || request != null) return;
            if (EditorApplication.isPlayingOrWillChangePlaymode) return;
            if (EditorApplication.isCompiling || EditorApplication.isUpdating)
            {
                EditorApplication.delayCall += Run;
                return;
            }

            var missing = MissingPackages();
            if (missing.Count > 0)
            {
                if (SessionState.GetBool(TriedInstallKey, false)) return;
                SessionState.SetBool(TriedInstallKey, true);
                Debug.Log($"Big Night Out setup: installing {string.Join(", ", missing)}. Unity will recompile; if it asks to restart for the new Input System, choose Yes.");
                request = Client.AddAndRemove(missing.ToArray(), null);
                EditorApplication.update += WaitForInstall;
                return;
            }

            var builder = Type.GetType("BigNightOut.EditorTools.SliceBuilder, BigNightOut.Editor");
            var yarnBridge = Type.GetType("BigNightOut.YarnBridge.YarnDialogueStarter, BigNightOut.Yarn");
            if (builder == null || yarnBridge == null)
            {
                Debug.LogWarning("Big Night Out setup: packages are installed but the game scripts have not compiled. Check the Console for red errors and send them to Claude.");
                return;
            }

            Debug.Log("Big Night Out setup: building the dorm hallway slice.");
            builder.GetMethod("Build")?.Invoke(null, null);
        }

        static List<string> MissingPackages()
        {
            var manifest = File.Exists(ManifestPath) ? File.ReadAllText(ManifestPath) : "";
            var missing = new List<string>();
            if (!manifest.Contains("\"com.unity.inputsystem\"")) missing.Add("com.unity.inputsystem");
            if (!manifest.Contains("\"com.unity.ugui\"")) missing.Add("com.unity.ugui");
            if (!manifest.Contains("\"dev.yarnspinner.unity\"")) missing.Add(YarnGitUrl);
            return missing;
        }

        static void WaitForInstall()
        {
            if (request == null || !request.IsCompleted) return;
            EditorApplication.update -= WaitForInstall;
            if (request.Status == StatusCode.Failure)
                Debug.LogError($"Big Night Out setup: package install failed: {request.Error?.message}. Yarn Spinner needs Git installed (git-scm.com). Then use Big Night Out > Run First-Time Setup Again.");
            request = null;
            // On success Unity recompiles and reloads, which runs Run() again from the constructor.
        }
    }
}
