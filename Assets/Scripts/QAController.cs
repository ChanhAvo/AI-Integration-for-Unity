using System.Collections;
using System.Text;
using UnityEngine;
using TMPro;
using UnityEngine.Networking;

public class QAController : MonoBehaviour
{
    public TMP_InputField questionInput;
    public TextMeshProUGUI answerText;
    public TextMeshProUGUI storyContextSource; 
    
    // replace with your key
    private string apiKey = "YOUR_GEMINI_API_KEY_HERE"; 
    private string apiUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent";

    public void AskQuestion()
    {
        string userQuestion = questionInput.text;
        string currentContext = storyContextSource.text; 

        if (string.IsNullOrEmpty(userQuestion)) return;

        answerText.text = "Thinking...";
        StartCoroutine(SendRequest(userQuestion, currentContext));
    }

    IEnumerator SendRequest(string question, string context)
    {   
        string prompt = $"Context: {context}. \n\n User Question: {question}. \n\n Task: Answer simply for a child in 1-2 sentences.";
        
        
        string safePrompt = prompt.Replace("\"", "'");
        string json = "{\"contents\":[{\"parts\":[{\"text\":\"" + safePrompt + "\"}]}]}";

        using (UnityWebRequest webRequest = new UnityWebRequest(apiUrl + "?key=" + apiKey, "POST"))
        {
            byte[] bodyRaw = Encoding.UTF8.GetBytes(json);
            webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
            webRequest.downloadHandler = new DownloadHandlerBuffer();
            webRequest.SetRequestHeader("Content-Type", "application/json");

            yield return webRequest.SendWebRequest();

            if (webRequest.result == UnityWebRequest.Result.Success)
            {
                // Simple parsing to get the text (Use a proper JSON parser in production)
                string result = webRequest.downloadHandler.text;
                int start = result.IndexOf("\"text\": \"") + 9;
                if (start > 8)
                {
                    int end = result.IndexOf("\"", start);
                    string cleanAnswer = result.Substring(start, end - start).Replace("\\n", "\n");
                    answerText.text = cleanAnswer;
                }
                else answerText.text = "Answer format error.";
            }
            else
            {
                answerText.text = "Error: " + webRequest.error;
            }
        }
    }
}