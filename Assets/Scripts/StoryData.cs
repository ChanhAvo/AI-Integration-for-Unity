using System.Collections.Generic;
using System;

[Serializable]
public class StoryData
{
    public string storyId;
    public string title;
    public string location;
    public List<PageData> pages;
}

[Serializable]
public class PageData
{
    public int pageNumber;
    public string part;
    public string text;
    public string imageFileName;
    public string audioFileName;
    
}