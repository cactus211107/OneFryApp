async function convertHEIC(file_heic) {
    let blobURL = URL.createObjectURL(file_heic);
    // convert "fetch" the new blob url
    let blobRes = await fetch(blobURL)
    // convert response to blob
    let blob = await blobRes.blob()
    // convert to PNG - response is blob
    let conversionResult = await heic2any({blob})
    // convert to blob url
    var url = URL.createObjectURL(conversionResult);
    return url
}