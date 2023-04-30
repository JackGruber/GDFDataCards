# Datacards for OPR GDF

Tool to create PDF data cards for Onepagerules (GFF).

<img src="img/datacard.png">

## Preperation

### Windows

- Download GDFDataCards from release page
- Store `GDFDataCards.exe` in a folder
- Create a subfolder `font` where `GDFDataCards.exe` is located
- Download [Rosa Sans](https://fontlibrary.org/en/font/rosa-sans) Font
- Unzip font and store the `*.ttf` files it in `fonts\rosa-sans`
- Start `GDFDataCards.exe`
- Copy Army info from OPR army forge with `Share as Text`
<br/>
<img src="img/opr_army_forge_txt1.png">
<img src="img/opr_army_forge_txt2.png">
- Past the text into `GDFDataCards.exe`

## Images on Datacard

To add images for the data cards, create an order `data\images` and store the image of the unit in it. The images must be named like the unit, but may only contain letters and numbers. Replace everything else with `_`.

Examples:

|Unit name|Filename|
|---|---|
|Storm Leader|Storm_Leader.png|
|2x Veteran|2x_Veteran.jpg|
