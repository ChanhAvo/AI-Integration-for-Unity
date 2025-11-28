using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using UnityEngine.Networking;
using System.Text.RegularExpressions;

public class StoryManager : MonoBehaviour
{
    [Header("Core UI")]
    public GameObject mainMenuPanel;
    public GameObject storyPanel;
    public GameObject qaWindow;

    [Header("Story Elements")]
    public RawImage displayImage;
    public TextMeshProUGUI displayText;
    public TextMeshProUGUI titleText;
    
    [Header("Navigation")]
    public Button nextButton;
    public Button prevButton;
    public Button replayButton;
    public Slider volumeSlider;
    public Button homeButton; 
    public Button openQAButton;
    public Button closeQAButton;

    [Header("Menu Elements")]
    public Transform menuGridContent; 
    public GameObject storyButtonPrefab;

    [Header("Audio")]
    public AudioSource voiceOverSource;

    private StoryData currentStory;
    private int currentPageIndex = 0;
    private string storyFolderPath;

    void Start()
    {
        // Setup Navigation
        nextButton.onClick.AddListener(NextPage);
        prevButton.onClick.AddListener(PrevPage);
        replayButton.onClick.AddListener(ReplayAudio);
        homeButton.onClick.AddListener(ShowMainMenu);
        
        // Setup Q&A Toggle
        openQAButton.onClick.AddListener(() => qaWindow.SetActive(true));
        closeQAButton.onClick.AddListener(() => qaWindow.SetActive(false));

        // Setup Audio
        volumeSlider.onValueChanged.AddListener(SetVolume);
        volumeSlider.value = 1.0f; // Default full volume

        // Generate Menu and Start
        GenerateStoryMenu();
        ShowMainMenu();
    }

    // Menu logic 
    void GenerateStoryMenu()
    {
        // 1. Clean up old buttons to prevent duplicates
        foreach (Transform child in menuGridContent) 
        {
            Destroy(child.gameObject);
        }

        // 2. Find all story folders in StreamingAssets
        string rootPath = Path.Combine(Application.streamingAssetsPath, "StoryData");
        if (!Directory.Exists(rootPath)) 
        {
            Debug.LogError("StoryData folder missing!");
            return;
        }

        string[] directories = Directory.GetDirectories(rootPath);

        // 3. Loop through each folder
        foreach (string dir in directories)
        {
            string folderName = new DirectoryInfo(dir).Name; // e.g., "story_01"
            string jsonPath = Path.Combine(dir, "story_data.json");

            // VALIDATION: Only add button if the JSON exists
            if (File.Exists(jsonPath))
            {
                try 
                {
                    // Read the JSON just to get the Title
                    string jsonContent = File.ReadAllText(jsonPath);
                    StoryData tempStory = JsonUtility.FromJson<StoryData>(jsonContent);
                    
                    // Use the real title from JSON, or folder name if title is missing
                    string displayName = !string.IsNullOrEmpty(tempStory.title) ? tempStory.title : folderName;

                    // Create the button from prefab
                    GameObject btnObj = Instantiate(storyButtonPrefab, menuGridContent);
                    
                    // Set the text
                    TextMeshProUGUI btnText = btnObj.GetComponentInChildren<TextMeshProUGUI>();
                    if (btnText != null) 
                    {
                        btnText.text = displayName;
                    }

                    // Add click listener
                    Button btn = btnObj.GetComponent<Button>();
                    btn.onClick.AddListener(() => {
                        LoadStory(folderName);
                        ShowStoryMode();
                    });
                }
                catch (System.Exception e)
                {
                    Debug.LogWarning("Skipping corrupted story: " + folderName + " Error: " + e.Message);
                }
            }
        }
    }

    void ShowMainMenu()
    {
        mainMenuPanel.SetActive(true);
        storyPanel.SetActive(false);
        if(qaWindow != null) qaWindow.SetActive(false);
        voiceOverSource.Stop();
    }

    void ShowStoryMode()
    {
        mainMenuPanel.SetActive(false);
        storyPanel.SetActive(true);
    }

    // --- STORY LOGIC ---
    public void LoadStory(string storyId)
    {
        string jsonPath = Path.Combine(Application.streamingAssetsPath, "StoryData", storyId, "story_data.json");
        storyFolderPath = Path.Combine(Application.streamingAssetsPath, "StoryData", storyId);

        if (File.Exists(jsonPath))
        {
            string jsonContent = File.ReadAllText(jsonPath);
            currentStory = JsonUtility.FromJson<StoryData>(jsonContent);

            if (titleText != null) titleText.text = currentStory.title;
            
            currentPageIndex = 0;
            LoadPage(currentPageIndex);
        }
    }

    void LoadPage(int index)
    {
        if (currentStory == null) return;
        PageData page = currentStory.pages[index];

        displayText.text = CleanText(page.text);

        string imgPath = Path.Combine(storyFolderPath, page.imageFileName);
        StartCoroutine(LoadImageTexture(imgPath));

        string audioPath = Path.Combine(storyFolderPath, page.audioFileName);
        StartCoroutine(PlayAudioClip(audioPath));

        prevButton.interactable = (index > 0);
        nextButton.interactable = (index < currentStory.pages.Count - 1);
    }

    void NextPage()
    {
        if (currentStory == null) return;
        if (currentPageIndex < currentStory.pages.Count - 1)
        {
            currentPageIndex++;
            LoadPage(currentPageIndex);
        }
    }

    void PrevPage()
    {
        if (currentPageIndex > 0)
        {
            currentPageIndex--;
            LoadPage(currentPageIndex);
        }
    }
    
    // --- AUDIO LOGIC ---
    public void ReplayAudio()
    {
        voiceOverSource.Stop();
        voiceOverSource.Play();
    }

    public void SetVolume(float vol)
    {
        voiceOverSource.volume = vol;
    }

    // --- HELPERS ---
    IEnumerator LoadImageTexture(string path)
    {
        using (UnityWebRequest uwr = UnityWebRequestTexture.GetTexture("file://" + path))
        {
            yield return uwr.SendWebRequest();
            if (uwr.result == UnityWebRequest.Result.Success)
                displayImage.texture = DownloadHandlerTexture.GetContent(uwr);
        }
    }

    IEnumerator PlayAudioClip(string path)
    {
        voiceOverSource.Stop();
        using (UnityWebRequest uwr = UnityWebRequestMultimedia.GetAudioClip("file://" + path, AudioType.MPEG))
        {
            yield return uwr.SendWebRequest();
            if (uwr.result == UnityWebRequest.Result.Success)
            {
                AudioClip clip = DownloadHandlerAudioClip.GetContent(uwr);
                voiceOverSource.clip = clip;
                voiceOverSource.Play();
            }
        }
    }

    string CleanText(string rawText)
    {
        return Regex.Replace(rawText, @"^Page \d+:\s*", "");
    }
}