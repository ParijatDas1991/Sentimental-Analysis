These are the steps to publish an app to the iOS App Store for the purposes of validation. 

### Motivation - why do this?

When we make architectural changes, it is critical that we validate those changes with the iOS App Store. We have seen that with local development, certain things work while those same things will be rejected by the App Store. At 100.11 we shipped libruntimecore.dylib for iOS which worked in all our tests, but was rejected by the App Store during final app approval and validation.

### Who can do this?

Only certain people can do this. There are numerous hoops to jump through to get this workflow working from start to finish.

### Contacts

 - James Ballard - can help with all steps
 - Nick Furness - only Nick can generate and share signing certificates or create an app profile to use for testing.

### Does this actually push an app to the App Store?

No. It pushes an app up to Test Flight that is never published any further. Test flight is an app beta testing service from Apple.

### What are the requirements?

1. The developer in question must be part of the "Esri" Apple developer group. "Esri Enterprise" is not enough as that group cannot push to the App Store.
2. The developer in question must have an app with a provisioning profile that available for uploads. This means that there must already be an app profile to use.
3. The developer must have the specific provisioning profile needed for the app.
4. The developer must have app signing certificate required to sign apps for the App Store.
5. The app's version must be incremented every time you publish it, or submit it for approval.

### Existing App Details

1. The App I use is called "ios_qml" with the exact Bundle Identifier of `com.esri.runtime.qt.ios-qml`. 
2. The provisioning profile is called "QML DLL Validation".
3. The Signing Certificate is "Apple Distribution: ESRI (75Z67E6SV2)" - this may change as the certificate expires.

### Steps to actually building this app and getting App Store approval

1. Open the project in question.
2. Run qmake.
3. Open the generated Xcode project with Xcode.

In the "General" build options tab, make sure "Any iOS Device (arm64)" is selected.

![Screen Shot 2021-05-18 at 1 30 16 PM](https://devtopia.esri.com/storage/user/166/files/c2df4680-b7dd-11eb-8303-ac4edef135ca)

Also, increment the version number as required. In the app's .pro file I keep a running list of submitted versions along with what is different. Be sure the Bundle Identifier is precise as required for the app.

In the "Signing & Capabilities", uncheck "Automatically manage signing". 

![Screen Shot 2021-05-18 at 1 30 25 PM](https://devtopia.esri.com/storage/user/166/files/c2df4680-b7dd-11eb-8690-049261201435)

Select the Provisioning Profile for the app and make sure the rest of the settings are correct.

4. Select "Archive" from the Product menu.

5. When complete, the Organizer should appear with the app.

![Screen Shot 2021-05-18 at 1 41 42 PM](https://devtopia.esri.com/storage/user/166/files/d0490080-b7de-11eb-8fe7-bb393d68af2c)

6. Select your latest build and then "Distribute App"

7. Follow through these dialogs and choose the defaults. In one screen, you will need to select the Profile if it's not selected.

![Screen Shot 2021-05-18 at 1 45 18 PM](https://devtopia.esri.com/storage/user/166/files/1fdbfc00-b7e0-11eb-8a89-4559bff90f32)
![Screen Shot 2021-05-18 at 1 45 29 PM](https://devtopia.esri.com/storage/user/166/files/223e5600-b7e0-11eb-8171-0b9fe6da7406)
![Screen Shot 2021-05-18 at 1 46 10 PM](https://devtopia.esri.com/storage/user/166/files/266a7380-b7e0-11eb-9fad-000a151d7cf3)
![Screen Shot 2021-05-18 at 1 46 20 PM](https://devtopia.esri.com/storage/user/166/files/28343700-b7e0-11eb-95c6-0e9200d1d9ed)
![Screen Shot 2021-05-18 at 1 45 40 PM](https://devtopia.esri.com/storage/user/166/files/2cf8eb00-b7e0-11eb-9df1-6f336d3b9327)
![Screen Shot 2021-05-18 at 1 45 49 PM](https://devtopia.esri.com/storage/user/166/files/2ff3db80-b7e0-11eb-91d8-54d0368048b8)
![Screen Shot 2021-05-18 at 1 46 36 PM](https://devtopia.esri.com/storage/user/166/files/32eecc00-b7e0-11eb-8823-49a624259696)
![Screen Shot 2021-05-18 at 1 49 40 PM](https://devtopia.esri.com/storage/user/166/files/35512600-b7e0-11eb-8f67-1e11b6926367)
![Screen Shot 2021-05-18 at 1 49 47 PM](https://devtopia.esri.com/storage/user/166/files/384c1680-b7e0-11eb-8c9e-74f51219f661)
![Screen Shot 2021-05-18 at 1 52 08 PM](https://devtopia.esri.com/storage/user/166/files/46019c00-b7e0-11eb-8ba3-c1e7a1afb67d)

8. Next, visit https://appstoreconnect.apple.com/apps/1561258181/testflight/ios or whatever the url for the specific app is.

9. View the Version info for the app you just uploaded.

![Screen Shot 2021-05-18 at 1 58 17 PM](https://devtopia.esri.com/storage/user/166/files/25861180-b7e1-11eb-9379-5ae07f38160d)

10. Next you should get an email from Apple at some point with any validation problems that arose. If the app succeeds validation, you may not get any email. In that case, proceed to the next step.

12. If you click on the version number (seen above with 1.0.5), it will take you to a separate page. On that page, click "Build Metadata" and check the "Binary State".

![Screen Shot 2021-05-18 at 2 00 06 PM](https://devtopia.esri.com/storage/user/166/files/6b42da00-b7e1-11eb-82de-fe9e3bdd4023)


## Test flight steps

Follow these additional steps to validate downloading and installing the app from test flight.

Click manage

![Screen Shot 2021-08-05 at 2 32 05 PM](https://devtopia.esri.com/storage/user/166/files/09cd2300-f5fa-11eb-8dbb-a1e38968c582)

Go through the following Export Compliance Steps:

![Screen Shot 2021-08-05 at 2 33 47 PM](https://devtopia.esri.com/storage/user/166/files/5b75ad80-f5fa-11eb-9ac5-72c3bf71c75e)

![Screen Shot 2021-08-05 at 2 33 58 PM](https://devtopia.esri.com/storage/user/166/files/62042500-f5fa-11eb-9349-5c90bb0364b8)

![Screen Shot 2021-08-05 at 2 34 11 PM](https://devtopia.esri.com/storage/user/166/files/70524100-f5fa-11eb-830c-46947c4f6824)

![Screen Shot 2021-08-05 at 2 34 34 PM](https://devtopia.esri.com/storage/user/166/files/806a2080-f5fa-11eb-8e76-aa8d96e50bae)

Once that is done, add any additional testers to the app's testers. They will be able to download the app via the iOS Test Flight app.

![76CD4B97-91C4-4A73-A269-A6E4E872DC98](https://devtopia.esri.com/storage/user/166/files/c32bf880-f5fa-11eb-8baa-dc17fef1cc0f)
