import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import crypto from 'crypto';


// Cloudinary Credentials
const CLOUD_NAME = 'dmbofhpcg';
const API_KEY = '485198976381662';
const API_SECRET = 'ssAiRIMFlklZT7cdX-W1lGS3rjI'
const UPLOAD_PRESET = 'bespoke-uploads';
const FOLDER_NAME = 'bespoke-tint-ppf-bellevue-car-wraps';


// Your array of images
export const images = [
  {
    "id": "17d7655d-722d-492b-b25a-212a50fee0c2",
    "url": "https://static.wixstatic.com/media/cd12f7_e991635a35b947498c5e66e6a049008d~mv2.jpg",
    "title": "Ferrari",
    "description": "Lots of pics of this one "
  },
  {
    "id": "bef360c4-f94a-4323-b7a0-0e844f6a15c6",
    "url": "https://static.wixstatic.com/media/cd12f7_f69518977feb4e0fb26109c631fcadf0~mv2.jpg",
    "title": "Ferrari",
    "description": ""
  },
  {
    "id": "936ef865-5042-4b17-ad6b-8cdc9be070ab",
    "url": "https://static.wixstatic.com/media/cd12f7_d785e4797d3449fe96eaa1bd39bc3ffb~mv2.jpg",
    "title": "Ferrari",
    "description": "Tinted"
  },
  {
    "id": "e6f014e3-0fff-418e-83b6-4902a11d0ee1",
    "url": "https://static.wixstatic.com/media/cd12f7_9fdf0e4bf3c24a478f28d11005a4a84a~mv2.jpg",
    "title": "Ferrari",
    "description": "Really close view of the 20%"
  },
  {
    "id": "dd936523-0f3b-4a56-973d-783a20fadc2a",
    "url": "https://static.wixstatic.com/media/cd12f7_8fbc81f32e9c452bb408fba7137a0ff2~mv2.jpg",
    "title": "Ferrari ",
    "description": "20% window tint "
  },
  {
    "id": "e85747df-8586-474e-b4d8-5366b54dc88b",
    "url": "https://static.wixstatic.com/media/cd12f7_698625736f8b4e7c80ee610c05d9f9db~mv2.jpg",
    "title": "2005 allroad ",
    "description": "There’s a special place in my heart for these cars 20%"
  },
  {
    "id": "18b3c725-5c72-44ee-ae04-c8e44e7bd4a5",
    "url": "https://static.wixstatic.com/media/cd12f7_d6f14b364ad0447fa151530d2792f9a0~mv2.jpg",
    "title": "2024 yukon ",
    "description": "window tint to match 20% "
  },
  {
    "id": "e02d39e9-68ea-4ecc-bfcc-2ca222b03159",
    "url": "https://static.wixstatic.com/media/cd12f7_826a3cb1ab364ab995c501ddde7b5a13~mv2.jpg",
    "title": "1995 r33 skyline ",
    "description": "Getting prepped for full body wrap "
  },
  {
    "id": "f46cc598-d7de-4d03-906a-1ce874547417",
    "url": "https://static.wixstatic.com/media/cd12f7_e82298a87e994da983a89c34d8bdbab6~mv2.jpg",
    "title": "1995 r33 skyline ",
    "description": "Getting closer for wrap "
  },
  {
    "id": "d4a1eb7a-dc0e-42fb-a883-352bc2271244",
    "url": "https://static.wixstatic.com/media/cd12f7_d6c6a8acf0ae42f1aa703ce286363895~mv2.jpg",
    "title": "1995 r33 skyline ",
    "description": "We made it atomic real 3m vinyl wrap "
  },
  {
    "id": "112f2769-2dc0-440d-8779-c87a93d54c11",
    "url": "https://static.wixstatic.com/media/cd12f7_15d9d1c81d5746ee82fbe39f28d7fad9~mv2.jpg",
    "title": "1995 r33 skyline",
    "description": "Tada it’s a wrap atomic real 3m"
  },
  {
    "id": "461d2e5e-2b5e-4a6e-83c3-5bb5044445ab",
    "url": "https://static.wixstatic.com/media/cd12f7_745e7a71069449ff88efdad9a880ef1a~mv2.jpeg",
    "title": "1995 r33 skyline",
    "description": ""
  },
  {
    "id": "1c884ce4-c778-4dd3-8d08-f85bcbb2f4fb",
    "url": "https://static.wixstatic.com/media/cd12f7_84bd9db32cab44c09d94413c6e6a1628~mv2.jpg",
    "title": "1995 r33 skyline",
    "description": ""
  },
  {
    "id": "1f797077-4901-4887-aaca-edbe2d71fa8c",
    "url": "https://static.wixstatic.com/media/cd12f7_4e3c9b5b82fc4018bef6faa147e32be5~mv2.jpg",
    "title": "Tesla Cybertruck",
    "description": ""
  },
  {
    "id": "4ddf027d-651c-4f74-9099-84783121635c",
    "url": "https://static.wixstatic.com/media/cd12f7_3c7a56a1f5cd419bb61fe7dffece6504~mv2.jpg",
    "title": "2024 corvette z06",
    "description": "full body clear ppf and 30% ceramic window tint."
  },
  {
    "id": "9bfb0c96-3d1d-4e83-9769-c290dce4e058",
    "url": "https://static.wixstatic.com/media/cd12f7_70798bec2de9447d8e7893b163683611~mv2.jpg",
    "title": "2024 tesla model x refresh ",
    "description": "full front clear bra/ ppf 2 front match 20% ceramic"
  },
  {
    "id": "4e7be7b7-c9e1-4864-bc14-5218d808db54",
    "url": "https://static.wixstatic.com/media/cd12f7_25f23644bf834c74a4c88b61b06acc94~mv2.jpg",
    "title": "2024 tesla model x refresh",
    "description": "better view of front end ppf and badge removal fora  cleaner look"
  },
  {
    "id": "8a6e9a3b-4de0-4e23-9d3f-2288ed45ddd7",
    "url": "https://static.wixstatic.com/media/cd12f7_2f8cbecf02d148ba84d568ab1a1e999a~mv2.jpg",
    "title": "2023 malibu ",
    "description": "20% ceramic window tint full shield. this was done off site "
  },
  {
    "id": "710548bc-3330-4587-b9b8-0943cfe9bc96",
    "url": "https://static.wixstatic.com/media/cd12f7_afb17a9464af40bfa6a3d861f15015ce~mv2.jpg",
    "title": "2024 malibu",
    "description": "better angle of the window tint 20% ceramic "
  },
  {
    "id": "b993c3ab-782f-4f5b-bd9f-c681fa446375",
    "url": "https://static.wixstatic.com/media/cd12f7_f935383960fd49c28bcf9ad226f07d8d~mv2.jpg",
    "title": "2024 centurion",
    "description": "20% full windcreen tint. this also was done off site "
  },
  {
    "id": "82683d8c-bd33-40ff-a606-56f7b2e06ca1",
    "url": "https://static.wixstatic.com/media/cd12f7_51717ec7a5af4b278957ff78b20ef74a~mv2.jpg",
    "title": "2024 centurion",
    "description": "farther angle of the 20% tint"
  },
  {
    "id": "df96954c-b819-4f02-8e3f-545b39fa8b85",
    "url": "https://static.wixstatic.com/media/cd12f7_1572b57ed4f649a9b3b6461d8d14c284~mv2.jpg",
    "title": "2024 Tesla model 3 refresh ",
    "description": "Full body clear PPF to protect all painted surfaces"
  },
  {
    "id": "e8863777-4642-4135-8436-9dbd1559b85e",
    "url": "https://static.wixstatic.com/media/cd12f7_befa2e499e9b4d0d886b6695620eb377~mv2.jpg",
    "title": "2024 Tesla model 3 refresh ",
    "description": "Another angle of the clarity of the ppf film "
  },
  {
    "id": "afb1bcc7-4092-4b55-9ed1-e160e73ac0c9",
    "url": "https://static.wixstatic.com/media/cd12f7_e822952555c64c3fbf443cf60daf0c53~mv2.jpg",
    "title": "2023 ford raptor ",
    "description": "Satin finish PPF full exterior body. taillight removed "
  },
  {
    "id": "879cc96f-ae1b-4668-b2e9-a77ef262bc6c",
    "url": "https://static.wixstatic.com/media/cd12f7_60a4ffd366274bdaa35efae9380a3058~mv2.jpg",
    "title": "2024 ford raptor ",
    "description": "Full body satin PPF window tint 20% all around "
  },
  {
    "id": "17d7655d-722d-492b-b25a-212a50fee0c2",
    "url": "https://static.wixstatic.com/media/cd12f7_e991635a35b947498c5e66e6a049008d~mv2.jpg",
    "title": "Ferrari",
    "description": "Lots of pics of this one "
  },
  {
    "id": "bef360c4-f94a-4323-b7a0-0e844f6a15c6",
    "url": "https://static.wixstatic.com/media/cd12f7_f69518977feb4e0fb26109c631fcadf0~mv2.jpg",
    "title": "IMG_0083.jpg",
    "description": ""
  },
  {
    "id": "936ef865-5042-4b17-ad6b-8cdc9be070ab",
    "url": "https://static.wixstatic.com/media/cd12f7_d785e4797d3449fe96eaa1bd39bc3ffb~mv2.jpg",
    "title": "Ferrari",
    "description": "Tinted"
  },
  {
    "id": "e6f014e3-0fff-418e-83b6-4902a11d0ee1",
    "url": "https://static.wixstatic.com/media/cd12f7_9fdf0e4bf3c24a478f28d11005a4a84a~mv2.jpg",
    "title": "Ferrari",
    "description": "Really close view of the 20%"
  },
  {
    "id": "dd936523-0f3b-4a56-973d-783a20fadc2a",
    "url": "https://static.wixstatic.com/media/cd12f7_8fbc81f32e9c452bb408fba7137a0ff2~mv2.jpg",
    "title": "Ferrari ",
    "description": "20% window tint "
  },
  {
    "id": "e85747df-8586-474e-b4d8-5366b54dc88b",
    "url": "https://static.wixstatic.com/media/cd12f7_698625736f8b4e7c80ee610c05d9f9db~mv2.jpg",
    "title": "2005 allroad ",
    "description": "There’s a special place in my heart for these cars 20%"
  },
  {
    "id": "18b3c725-5c72-44ee-ae04-c8e44e7bd4a5",
    "url": "https://static.wixstatic.com/media/cd12f7_d6f14b364ad0447fa151530d2792f9a0~mv2.jpg",
    "title": "2024 yukon ",
    "description": "window tint to match 20% "
  },
  {
    "id": "e02d39e9-68ea-4ecc-bfcc-2ca222b03159",
    "url": "https://static.wixstatic.com/media/cd12f7_826a3cb1ab364ab995c501ddde7b5a13~mv2.jpg",
    "title": "1995 r33 skyline ",
    "description": "Getting prepped for full body wrap "
  },
  {
    "id": "f46cc598-d7de-4d03-906a-1ce874547417",
    "url": "https://static.wixstatic.com/media/cd12f7_e82298a87e994da983a89c34d8bdbab6~mv2.jpg",
    "title": "1995 r33 skyline ",
    "description": "Getting closer for wrap "
  },
  {
    "id": "d4a1eb7a-dc0e-42fb-a883-352bc2271244",
    "url": "https://static.wixstatic.com/media/cd12f7_d6c6a8acf0ae42f1aa703ce286363895~mv2.jpg",
    "title": "1995 r33 skyline ",
    "description": "We made it atomic real 3m vinyl wrap "
  },
  {
    "id": "112f2769-2dc0-440d-8779-c87a93d54c11",
    "url": "https://static.wixstatic.com/media/cd12f7_15d9d1c81d5746ee82fbe39f28d7fad9~mv2.jpg",
    "title": "1995 r33 skyline ",
    "description": "Tada it’s a wrap atomic real 3m"
  },
  {
    "id": "461d2e5e-2b5e-4a6e-83c3-5bb5044445ab",
    "url": "https://static.wixstatic.com/media/cd12f7_745e7a71069449ff88efdad9a880ef1a~mv2.jpeg",
    "title": "IMG_0292.HEIC",
    "description": ""
  },
  {
    "id": "1c884ce4-c778-4dd3-8d08-f85bcbb2f4fb",
    "url": "https://static.wixstatic.com/media/cd12f7_84bd9db32cab44c09d94413c6e6a1628~mv2.jpg",
    "title": "IMG_0306.jpg",
    "description": ""
  },
  {
    "id": "1f797077-4901-4887-aaca-edbe2d71fa8c",
    "url": "https://static.wixstatic.com/media/cd12f7_4e3c9b5b82fc4018bef6faa147e32be5~mv2.jpg",
    "title": "IMG_0316.jpg",
    "description": ""
  },
  {
    "id": "4ddf027d-651c-4f74-9099-84783121635c",
    "url": "https://static.wixstatic.com/media/cd12f7_3c7a56a1f5cd419bb61fe7dffece6504~mv2.jpg",
    "title": "2024 corvette z06",
    "description": "full body clear ppf and 30% ceramic window tint."
  },
  {
    "id": "9bfb0c96-3d1d-4e83-9769-c290dce4e058",
    "url": "https://static.wixstatic.com/media/cd12f7_70798bec2de9447d8e7893b163683611~mv2.jpg",
    "title": "2024 tesla model x refresh ",
    "description": "full front clear bra/ ppf 2 front match 20% ceramic"
  },
  {
    "id": "4e7be7b7-c9e1-4864-bc14-5218d808db54",
    "url": "https://static.wixstatic.com/media/cd12f7_25f23644bf834c74a4c88b61b06acc94~mv2.jpg",
    "title": "2024 tesla model x refresh",
    "description": "better view of front end ppf and badge removal fora  cleaner look"
  },
  {
    "id": "8a6e9a3b-4de0-4e23-9d3f-2288ed45ddd7",
    "url": "https://static.wixstatic.com/media/cd12f7_2f8cbecf02d148ba84d568ab1a1e999a~mv2.jpg",
    "title": "2023 malibu ",
    "description": "20% ceramic window tint full shield. this was done off site "
  },
  {
    "id": "710548bc-3330-4587-b9b8-0943cfe9bc96",
    "url": "https://static.wixstatic.com/media/cd12f7_afb17a9464af40bfa6a3d861f15015ce~mv2.jpg",
    "title": "2024 malibu",
    "description": "better angle of the window tint 20% ceramic "
  },
  {
    "id": "b993c3ab-782f-4f5b-bd9f-c681fa446375",
    "url": "https://static.wixstatic.com/media/cd12f7_f935383960fd49c28bcf9ad226f07d8d~mv2.jpg",
    "title": "2024 centurion",
    "description": "20% full windcreen tint. this also was done off site "
  },
  {
    "id": "82683d8c-bd33-40ff-a606-56f7b2e06ca1",
    "url": "https://static.wixstatic.com/media/cd12f7_51717ec7a5af4b278957ff78b20ef74a~mv2.jpg",
    "title": "2024 centurion",
    "description": "farther angle of the 20% tint"
  },
  {
    "id": "df96954c-b819-4f02-8e3f-545b39fa8b85",
    "url": "https://static.wixstatic.com/media/cd12f7_1572b57ed4f649a9b3b6461d8d14c284~mv2.jpg",
    "title": "2024 Tesla model 3 refresh ",
    "description": "Full body clear PPF to protect all painted surfaces"
  },
  {
    "id": "e8863777-4642-4135-8436-9dbd1559b85e",
    "url": "https://static.wixstatic.com/media/cd12f7_befa2e499e9b4d0d886b6695620eb377~mv2.jpg",
    "title": "2024 Tesla model 3 refresh ",
    "description": "Another angle of the clarity of the ppf film "
  },
  {
    "id": "afb1bcc7-4092-4b55-9ed1-e160e73ac0c9",
    "url": "https://static.wixstatic.com/media/cd12f7_e822952555c64c3fbf443cf60daf0c53~mv2.jpg",
    "title": "2023 ford raptor ",
    "description": "Satin finish PPF full exterior body. taillight removed "
  },
  {
    "id": "879cc96f-ae1b-4668-b2e9-a77ef262bc6c",
    "url": "https://static.wixstatic.com/media/cd12f7_60a4ffd366274bdaa35efae9380a3058~mv2.jpg",
    "title": "2024 ford raptor ",
    "description": "Full body satin PPF window tint 20% all around "
  },
  {
    "id": "eb12ab70-b815-4e95-b141-42b3c2481087",
    "url": "https://static.wixstatic.com/media/cd12f7_193f695b1382417ba9ba235f238f484a~mv2.jpg",
    "title": "2023 ford raptor ",
    "description": "outside pic of full body satin ppf/ clear bra "
  },
  {
    "id": "3e51f982-32b0-4bf7-9675-0856e0a4851a",
    "url": "https://static.wixstatic.com/media/cd12f7_6f7d266a797544a7b00917c98ebd3e82~mv2.jpg",
    "title": "2023 corvette and 2022 Chevy 3500hd ",
    "description": "Corvette is full body clear PPF or clear bra. The truck is protected with a satin finish PPF. Both are fully “wrapped”/ protected "
  },
  {
    "id": "43b9c1d2-dfc6-4590-9e4c-96da227ae57a",
    "url": "https://static.wixstatic.com/media/cd12f7_33155d93e5d84dc68f75afbe7ef3e57c~mv2.jpg",
    "title": "Cybertruck foundation 2024 ",
    "description": "Full body stek dynomatt black. PPF color change "
  },
  {
    "id": "579a2b7c-97e4-45b1-9d89-d4fa9323ac0f",
    "url": "https://static.wixstatic.com/media/cd12f7_87fda14508ff48abbd499078b2118aa9~mv2.jpg",
    "title": "2024 cybertruck foundation ",
    "description": "Protected in style. Stek dynomatt black PPF wrap"
  },
  {
    "id": "c532d118-25e2-4909-b43a-8f27ab2ef05b",
    "url": "https://static.wixstatic.com/media/cd12f7_47dcf3c0673d45548c4058738a7522ff~mv2.jpg",
    "title": "2024 cybertruck foundation ",
    "description": "Stek dynomatt black ppf "
  },
  {
    "id": "4a6a490a-d413-4a5f-8078-1d4a21965fa0",
    "url": "https://static.wixstatic.com/media/cd12f7_8607d823c97b4f7b9057dc25f5a982b7~mv2.jpg",
    "title": "2024 Supra ",
    "description": "Full body stek dyno purple clear bra/fashion film"
  },
  {
    "id": "54821dcd-9389-4275-ad23-5462e896f949",
    "url": "https://static.wixstatic.com/media/cd12f7_09d805a5a73243ecb58fe7a6bb29c52d~mv2.jpg",
    "title": "2024 corvette z06 c8-r carbon package ",
    "description": "Full front clear bra/ppf ceramic coat"
  },
  {
    "id": "ac67d1cd-790f-4de1-82bb-0021fa115825",
    "url": "https://static.wixstatic.com/media/cd12f7_d5a689ae79404acc8b8242d5f0051b64~mv2.jpg",
    "title": "2016 btw m6 grand coupe",
    "description": "Full front clear bra and creaic coat"
  },
  {
    "id": "b5e274de-9635-4d50-91a3-8482d8f9848f",
    "url": "https://static.wixstatic.com/media/cd12f7_4cca27ef7027495c98ae587a6bed26e1~mv2.jpg",
    "title": "2024 Tesla cybertrck ",
    "description": "Satin black vinyl and 2 front tint "
  },
  {
    "id": "493fcb10-4c1e-4e3d-8533-69a2c4f5034c",
    "url": "https://static.wixstatic.com/media/cd12f7_153ab1fcebaa487aa5e2a2441dc91dd1~mv2.jpg",
    "title": "2024 Tesla model y ",
    "description": "In process for satin PPF "
  },
  {
    "id": "7d389a6b-7e59-43c4-98b2-68c9ce181f82",
    "url": "https://static.wixstatic.com/media/cd12f7_73f387503b32492daadc21ba414268e3~mv2.jpg",
    "title": "2024 Tesla model y ",
    "description": "Full body satin PPF finish 20% 2 fronts 50% windshield "
  },
  {
    "id": "4c47e6e2-2c50-4000-bc81-4d48156b5f17",
    "url": "https://static.wixstatic.com/media/cd12f7_fd4df5fca4c349f7b7cddf7ee7b66c09~mv2.jpg",
    "title": "2024 Ferrari 296 gtb",
    "description": "Full body clear bra "
  },
  {
    "id": "19f8f53b-d0ae-4275-a33a-caeea0bba498",
    "url": "https://static.wixstatic.com/media/cd12f7_7d4bfe686e3f4f8095b7faed8a2ed4ea~mv2.jpg",
    "title": "Kris looking good in his blouse ",
    "description": "Prepped and ready for ceramic coating "
  },
  {
    "id": "f2adb55f-00ba-4115-bb04-18d79f8e8930",
    "url": "https://static.wixstatic.com/media/cd12f7_e7c928b01d514de8bc56b91922782db6~mv2.jpg",
    "title": "2024 cybertruck tint with windshield ",
    "description": "tinted windshield 70% ceramic, matched front windows to rear 20% ceramic "
  },
  {
    "id": "49d5726a-36a7-450c-929a-19eea87725e2",
    "url": "https://static.wixstatic.com/media/cd12f7_4ff2d29e12594679bf56396bd7d79424~mv2.jpg",
    "title": "2024 Corolla gr full front clear bra/ ppf",
    "description": "full front end ppf and roof clear bra/ ppf"
  },
  {
    "id": "42db5880-69be-478e-9c2a-671b13d17349",
    "url": "https://static.wixstatic.com/media/cd12f7_3c5f89a0ad0244ec8b0459ce7ec0f633~mv2.png",
    "title": "2023 Toyota Tundra ",
    "description": "Full front Paint protection/ clear bra, full tint & windscreen"
  },
  {
    "id": "74f1d085-09e6-4798-adb0-e6d593a3f878",
    "url": "https://static.wixstatic.com/media/cd12f7_43e2424d4a3e427d855363651f258700~mv2.jpg",
    "title": "2021 Ford Raptor ",
    "description": "Stek Dyno-grey full body. paint protection film, 2 front windows 20% Ceramic tint "
  },
  {
    "id": "6d9a89c6-fdf2-45d4-9539-cd65b8f0ffbc",
    "url": "https://static.wixstatic.com/media/cd12f7_03e3466653ef416da2e80a2302a101b9~mv2.jpg",
    "title": "2022 Porsche Taycan ",
    "description": "Full body Paint Protection film in clear 10 year warranty film tinted 15% sides and 50% windscreen "
  },
  {
    "id": "2853bdb3-8609-42a9-8268-d294892a2864",
    "url": "https://static.wixstatic.com/media/cd12f7_3ac8bbe82c484547a1e413bf02c2d6dc~mv2.jpg",
    "title": "2017 Audi s5 ",
    "description": "3m Matte Military green Vinyl color change wrap Blackout trim wiht 3m gloss black, window tint 20% sides and rear "
  },
  {
    "id": "7d2a6942-d59c-4196-8c53-b199f40d825c",
    "url": "https://static.wixstatic.com/media/cd12f7_b5e1c893136a414b87967fe95e81e512~mv2.jpg",
    "title": "2022 Porsche Taycan",
    "description": "Full body clear Paint Protection Film. Protect your investment "
  },
  {
    "id": "2f200467-78df-41ea-bd18-cbc7542f6c96",
    "url": "https://static.wixstatic.com/media/cd12f7_549dc950edab48449270da25792fcd68~mv2.jpg",
    "title": "not sure of the year but its a Rossian",
    "description": "Full Front end Paint Protection Film "
  },
  {
    "id": "4d203967-6cb2-43c0-980a-119beb232d0a",
    "url": "https://static.wixstatic.com/media/cd12f7_32f920d6511540a29f6a6d3e8426102f~mv2.jpg",
    "title": "2022 Chevy 3500HD ",
    "description": "Full body Satin finish Paint protection film/ clear bra "
  },
  {
    "id": "c6b328b5-b891-4e35-83bb-2ba7ea294d7b",
    "url": "https://static.wixstatic.com/media/cd12f7_cf794ae40ef942ecafad6686cdeecb7a~mv2.jpg",
    "title": "2023 Lucid",
    "description": "Full Body clear bra/ paint protection film, windows tinted 20%"
  },
  {
    "id": "ffddadaa-eb17-4906-92ee-a4739f426227",
    "url": "https://static.wixstatic.com/media/cd12f7_f364dbcd40604953b191d766ee4ac3cb~mv2.jpg",
    "title": "2022 Chevy 3500HD ",
    "description": "full body satin finish/ stealth finish paint protection film"
  },
  {
    "id": "242ed5e5-0d1a-451b-bd06-6dac45db5f35",
    "url": "https://static.wixstatic.com/media/cd12f7_a8b0eb0a498744e1a70e869ec5b946cc~mv2.jpg",
    "title": "2020 A20 i believe... ",
    "description": "15% tint on windscreen "
  },
  {
    "id": "bbd63f66-5444-49a6-a8de-a02b2dd32d2f",
    "url": "https://static.wixstatic.com/media/cd12f7_25c2828bab0a4903804e7adddabe0757~mv2.jpg",
    "title": "2017 Audi S6",
    "description": "Stealth/ Satin finish Paint Protection Film 20% tint "
  },
  {
    "id": "763a08eb-b466-4dd1-8751-0a82910c3000",
    "url": "https://static.wixstatic.com/media/cd12f7_a96cecd365754d7d955629930faaa80d~mv2.jpg",
    "title": "2015 Bmw I8",
    "description": "Full Body clear finish Paint Protection Film, 15% tint sides and rear 70% windscreen, Ceramic Coated "
  },
  {
    "id": "a3527cc4-cda5-4183-956c-ac63adc1b32e",
    "url": "https://static.wixstatic.com/media/cd12f7_2d9ee9a84b084739bfdc329ee925046d~mv2.jpg",
    "title": "2022 Tesla model s PLAID",
    "description": "Full body clear paint protection film tinted 35% windscreen 15% sides and rear, Ceramic Coated"
  },
  {
    "id": "f46079cc-9743-4644-8911-d3e797b16bee",
    "url": "https://static.wixstatic.com/media/cd12f7_abd95f28b2984d0abde5c6798b75c6f8~mv2.jpg",
    "title": "cls63 amg",
    "description": "30% tint 3M film"
  },
  {
    "id": "98dc1dc2-7398-49f1-88ba-48325e6e7dc1",
    "url": "https://static.wixstatic.com/media/cd12f7_d4489a1ed14f4b99945edc880387bafd~mv2.jpg",
    "title": "Jeep trackhawk",
    "description": "3M Matte metallic color change "
  },
  {
    "id": "0866cf19-1545-4588-acc8-182145b0c609",
    "url": "https://static.wixstatic.com/media/cd12f7_a87ea7707ba541b4a9791479432cc0ad~mv2.jpg",
    "title": "2020 jeep trackhawk",
    "description": "full 3M matte metallic grey"
  },
  {
    "id": "f320835d-cf91-4cc7-9ab8-d3b977259423",
    "url": "https://static.wixstatic.com/media/cd12f7_eced0456f88243fe8b720305d2cfcc11~mv2.jpg",
    "title": "Honda del sol ",
    "description": "Full 3M volcanic flare flip color on this fully built turbo honda "
  },
  {
    "id": "35de7e2a-118d-440c-a27a-484d71726101",
    "url": "https://static.wixstatic.com/media/cd12f7_1957ce32245b4a5bb0396a639d4dd62f~mv2.jpg",
    "title": "honda del sol",
    "description": "tinted windshield 50% 15% sides and rear 3M volcanic flare vinyl wrap installed"
  },
  {
    "id": "bd26bade-0870-4c45-b80c-c788e92f1e76",
    "url": "https://static.wixstatic.com/media/cd12f7_a880e60146ad48428f54c77cc2e85920~mv2.jpg",
    "title": "audi s3 ",
    "description": "full 3M matte military green vinyl wrap "
  },
  {
    "id": "ffb08a8e-222e-4cf2-9810-58e2a9533c88",
    "url": "https://static.wixstatic.com/media/cd12f7_1206c7cfcf6b43adaa44fee1ac6ffe2c~mv2.jpg",
    "title": "2023 Volvo xc90",
    "description": "Stek Dyno-Prism full body Paint protection film/ colorshift, 20% Ceramic tint on front windows to match the rear "
  },
  {
    "id": "23d06d16-c85e-49a4-9887-c260817addbf",
    "url": "https://static.wixstatic.com/media/cd12f7_3840b51a95f24c8fa5ac4a326f82a65d~mv2.jpg",
    "title": "ferrari 3 teslas ",
    "description": "ferrari 458 italia getting full front clear bra/ppf (paint protection film), and satin black roof and side skirts all 3 teslas getting the same treatment "
  },
  {
    "id": "63c04581-5558-40c4-8bc7-232a59628561",
    "url": "https://static.wixstatic.com/media/cd12f7_5c0a999a0d0e4e2092d9e9b0ce50ed27~mv2.jpg",
    "title": "nissan maxima",
    "description": "headlight restoration"
  },
  {
    "id": "e3aa6ff6-fdec-410b-9687-58262d56b559",
    "url": "https://static.wixstatic.com/media/cd12f7_7c4da2b4c35c42b295c6dfc754b1e331~mv2.jpg",
    "title": "r35 gtr ",
    "description": "tinted 20% Ceramic "
  },
  {
    "id": "432fff05-1db0-45f7-ba69-234bc474cfaa",
    "url": "https://static.wixstatic.com/media/cd12f7_39e818e7776240028e3ab7457291dafc~mv2.jpg",
    "title": "2017 Audi s5 ",
    "description": "we are mid way wrappping this car in 3m matte military green bumper is removed in this pic as well"
  },
  {
    "id": "c95f308e-9f21-46f4-b3b5-bbf69c5b23fb",
    "url": "https://static.wixstatic.com/media/cd12f7_08ba7bb2e2d14247b7d2144e8d714357~mv2.jpg",
    "title": "2017 Audi S5 ",
    "description": "this is a full obdy wrap matte military green, when i wrap your vehicle it does come apart so i can wrap all edges and make it look factory aas possible so you dont see old body color at different angles, just goes to show this is passion for me more than it is a job."
  },
  {
    "id": "21c989e0-0065-4b9e-8528-2d9224fdaf3c",
    "url": "https://static.wixstatic.com/media/cd12f7_3a43c044a37c4188898a3ae2130c707b~mv2.jpg",
    "title": "fire truck ",
    "description": "we did ppf on the front of this firetruck so its easier for the firemen to clean. "
  },
  {
    "id": "ac592726-eddc-4251-9e67-a7a59a687f39",
    "url": "https://static.wixstatic.com/media/cd12f7_5c73e0baa06f415da36f60a4aca91934~mv2.jpg",
    "title": "2022",
    "description": "tinted this corvette 20% sides and wrapped the roof gloss black "
  },
  {
    "id": "24f88bc2-a4d2-42bc-9384-fe3a725f6e99",
    "url": "https://static.wixstatic.com/media/cd12f7_f04353b043664b2991ea0a3057cd9bc4~mv2.jpg",
    "title": "2022",
    "description": "Audi e-tron before i started tinting it just wiped it down so far"
  },
  {
    "id": "bcfa7a69-0006-4528-bd0a-18acb0868dce",
    "url": "https://static.wixstatic.com/media/cd12f7_101225a0177349e1b56c8f0a839614c0~mv2.jpg",
    "title": "2023 Audi E-TRON ",
    "description": "pulling this e-tron in for full front end paint protection film and tint "
  },
  {
    "id": "093fa4ba-1438-407b-881d-e1f1f7776654",
    "url": "https://static.wixstatic.com/media/cd12f7_ebc4615bd98b477ebe2b24def0ba03ee~mv2.jpg",
    "title": "1988 gti",
    "description": "80% windshield 80% ceramic sides and rear. super clean older car "
  },
  {
    "id": "a78bf7ad-3f25-4d15-ad79-1007db84365a",
    "url": "https://static.wixstatic.com/media/cd12f7_d38f12ffea584f359f003cc6c4b111e9~mv2.jpg",
    "title": "Stek demascus mirror cap PPF ",
    "description": ""
  },
  {
    "id": "1086d743-85c0-4b9e-84dd-90db81950941",
    "url": "https://static.wixstatic.com/media/cd12f7_4b70092ee80547e1a84973f320c14387~mv2.jpg",
    "title": "porsche 911",
    "description": "tinted 20% sides and rear, Full body clear paint protection film as well"
  },
  {
    "id": "084f1239-ba00-4013-acd0-f2dae543effc",
    "url": "https://static.wixstatic.com/media/cd12f7_b3f2b9d3c8c6469dbc6a0203c5e52842~mv2.jpg",
    "title": "porsche 911",
    "description": "tinted sides and rear 20% 70% windscreen, Full body clear Paint protection film as well "
  },
  {
    "id": "bdfbb094-79d2-46fa-bdd3-ce5a03eb00f4",
    "url": "https://static.wixstatic.com/media/cd12f7_65284fcb2fa546aebd52aa8926f35f9c~mv2.jpg",
    "title": "porsche 911",
    "description": "Full body clear paint protection film 20% rear glass"
  },
  {
    "id": "76749c43-3eaf-41f0-9c41-11db2da05615",
    "url": "https://static.wixstatic.com/media/cd12f7_bf6e19cd7c88467fa86ff47e9c75b5be~mv2.jpg",
    "title": "Clear PPF over a side car for clients pupper",
    "description": ""
  },
  {
    "id": "2d2317fb-74fd-4ccf-891b-1cf27482978a",
    "url": "https://static.wixstatic.com/media/cd12f7_e1e02628698c40f8bedffa61bf9034b9~mv2.jpg",
    "title": "ford raptor",
    "description": "stek dyno-grey paint protection film install, this one required full tear down as well its a color change "
  },
  {
    "id": "37c115e6-a0cd-47bf-8430-45e51287e827",
    "url": "https://static.wixstatic.com/media/cd12f7_68610a3c29f741a696c682d7032ddf98~mv2.jpg",
    "title": "Audi rsq8",
    "description": "20% 2 fronts to match the rear 70% windscreen "
  },
  {
    "id": "fad3c6bd-879c-4bb2-9179-23a5cc86efb1",
    "url": "https://static.wixstatic.com/media/cd12f7_560a306c4ce94cd9baf1f53ebbeb0098~mv2.jpg",
    "title": "Audi a5",
    "description": "tinted 30% ceramic "
  },
  {
    "id": "8f7f09e9-8bd8-4c62-abf4-84a862d57efe",
    "url": "https://static.wixstatic.com/media/cd12f7_ca76c763d6b744d69eb35f36471b8557~mv2.jpg",
    "title": "Audi a5",
    "description": "30% ceramic tint"
  },
  {
    "id": "e673fce3-e881-4550-88b6-6741cb651ed2",
    "url": "https://static.wixstatic.com/media/cd12f7_255f9d3dd6044b10a2e3b43f16181ade~mv2.jpg",
    "title": "91 boat",
    "description": "windscreen tint 30%"
  },
  {
    "id": "964cead1-459e-4ba6-b6ea-5daaa3488582",
    "url": "https://static.wixstatic.com/media/cd12f7_a1c900fb62da4e0b9293f9bd23c2e420~mv2.jpg",
    "title": "91 boat ",
    "description": "30% tint "
  },
  {
    "id": "ae21b63d-be19-49d2-8348-f7326eed1450",
    "url": "https://static.wixstatic.com/media/cd12f7_56b742669b084cde9221d94e053210ad~mv2.jpg",
    "title": "91 boat ",
    "description": "kris heating out the edge of this windscreen finish process"
  },
  {
    "id": "109df84c-d3f3-41c9-9840-b579ac4b5713",
    "url": "https://static.wixstatic.com/media/cd12f7_2932e7fae397400f812a3f42c77c9c3b~mv2.jpg",
    "title": "91 boat",
    "description": "kris starting the tint process "
  },
  {
    "id": "18fd3572-1d9d-4a42-baa2-bb95a2969519",
    "url": "https://static.wixstatic.com/media/cd12f7_a0bf213c43e14cbc83a3f883debe3c02~mv2.jpg",
    "title": "91 boat",
    "description": "kris having a chat with client.. hes slackin as we can all see"
  },
  {
    "id": "6d07bb6b-73c8-41df-a35e-542e273203ae",
    "url": "https://static.wixstatic.com/media/cd12f7_8a4709887e324b6b83e6fee896ab34b7~mv2.jpg",
    "title": "2017 audi s6 and gtr ",
    "description": "satin black gtr in vinyl and satin wrapped s6 in stealth ppf "
  },
  {
    "id": "81dbf0c0-05a7-4ab7-9309-537332b91587",
    "url": "https://static.wixstatic.com/media/cd12f7_3d88b4c9f20643c5958853b7afbbfe29~mv2.jpg",
    "title": "Satin black r35 Gtr 20% tint ",
    "description": ""
  },
  {
    "id": "f7940add-c9c2-4907-a4ce-e1801a6a6a92",
    "url": "https://static.wixstatic.com/media/cd12f7_54e0e7bc59ca49608909361e114451c9~mv2.jpg",
    "title": "tesla model y and gtr",
    "description": "tesla getting full body ppf/ gtr getting 20% tint"
  },
  {
    "id": "22fdfe78-3899-4495-8004-d58483b17782",
    "url": "https://static.wixstatic.com/media/cd12f7_290fef66ce8145d581d136de717db5ef~mv2.jpg",
    "title": "gtr",
    "description": "20% tint "
  },
  {
    "id": "7775366f-9d88-4d2d-88b3-0385498262cc",
    "url": "https://static.wixstatic.com/media/cd12f7_af5fa196b6134a02aef5541c32fc4ef6~mv2.jpg",
    "title": "aston martin",
    "description": "full front ppf you can see we wrap all edges as a standard "
  },
  {
    "id": "970db2a2-60a3-45f7-9883-fdb7fdbca5ba",
    "url": "https://static.wixstatic.com/media/cd12f7_9cd7f69f22dc4e1f9fb0f8c635397a39~mv2.jpg",
    "title": "aston martin",
    "description": "more edge wrapping "
  },
  {
    "id": "15d0ea22-2ad0-4677-ac49-9808d1a2de69",
    "url": "https://static.wixstatic.com/media/cd12f7_ccaa8e2e67d64c73b52b6ef687798f12~mv2.jpg",
    "title": "aston martin",
    "description": "i think i liked this car (kris) so i took alot of photos of it. "
  },
  {
    "id": "f13b0943-c77c-41eb-84e5-80bbae487e61",
    "url": "https://static.wixstatic.com/media/cd12f7_525db4434d1e48d282342f226d78ec14~mv2.png",
    "title": "gti",
    "description": "um.... im (kris) installing chrome tint per client request "
  },
  {
    "id": "654bf6f3-f4df-4efb-9502-b725eddbf763",
    "url": "https://static.wixstatic.com/media/cd12f7_4fad6667809a48d4a0fe52e609c302d5~mv2.png",
    "title": "ford focus st",
    "description": "windshield tint 35%"
  },
  {
    "id": "f23ca69e-44f0-44dd-b991-a3a0e7893e7b",
    "url": "https://static.wixstatic.com/media/cd12f7_7b551377cf814a6aa988b43ec3def15a~mv2.png",
    "title": "05 audi allroad/ charger ",
    "description": "tinted headlights on the charger"
  },
  {
    "id": "3c598b38-6b88-4977-9264-f133230cf2dc",
    "url": "https://static.wixstatic.com/media/cd12f7_1c2b123d7d14475a8303617835b80834~mv2.png",
    "title": "jeep wrangler ",
    "description": "before i started to tint it "
  },
  {
    "id": "071e1153-012f-40af-806d-4119f719db70",
    "url": "https://static.wixstatic.com/media/cd12f7_c217aa8ffb8340798f753e8c4b5498b5~mv2.png",
    "title": "05 allroad / audi r8",
    "description": "my allroad is faster... -_- allroad getting ready for passion red vinyl wrap, Audi r8 is getting full body clear paint protection film install"
  },
  {
    "id": "b3231b83-a63c-43d8-84e9-d7a8771e2bf6",
    "url": "https://static.wixstatic.com/media/cd12f7_f71b7fbefe7548d995ca175ed2fe81ff~mv2.jpg",
    "title": "Audi s6/ Audi allroad",
    "description": "my audi s6 looking pretty with its stealth paint protection film/ my audi allroad after it was wrapped in passion red. "
  },
  {
    "id": "6d763fce-7ff5-4b32-bfe2-5a80a09077a6",
    "url": "https://static.wixstatic.com/media/cd12f7_25c2828bab0a4903804e7adddabe0757~mv2.jpg",
    "title": "Satin PPF over gloss Audi s6 ",
    "description": ""
  },
  {
    "id": "94f4bd13-8a70-4b1b-bf78-e1321672893e",
    "url": "https://static.wixstatic.com/media/cd12f7_7774bf8727eb4c2889d4a5f9f49190ce~mv2.jpg",
    "title": "Full body satin PPF Audi s6",
    "description": ""
  },
  {
    "id": "b3d1a139-5497-43ed-80fa-34d3916595ca",
    "url": "https://static.wixstatic.com/media/cd12f7_4c83710dff82479dbac96e3654171cba~mv2.jpg",
    "title": "tesla model 3/ model y ",
    "description": "tesla getting wheels powder coated and full body ppf/ white tesla same thing full body ppf "
  },
  {
    "id": "13a85284-a840-437f-a37b-f8bf155094bc",
    "url": "https://static.wixstatic.com/media/cd12f7_f976d1ada3a34091a5b7b7c30b3a0476~mv2.jpg",
    "title": "Satin PPF lucid air going home ",
    "description": ""
  },
  {
    "id": "98390c35-acfa-44a6-9d8a-212331f44d6f",
    "url": "https://static.wixstatic.com/media/cd12f7_f2a8be05af0a4fc6a4bec378db1dff03~mv2.jpg",
    "title": "lucid",
    "description": "full body satin bottom half ppf and clear top half "
  },
  {
    "id": "f2bd3579-7b4d-463a-837a-a0188c83024e",
    "url": "https://static.wixstatic.com/media/cd12f7_8967c1574bc6478ab0141c7974538caa~mv2.jpg",
    "title": "Ceramic coated 2000 c5 corvette 50% windshield tint 5% sides and rear ",
    "description": ""
  },
  {
    "id": "9c9235c6-a8a5-4fb5-8429-f762fd0d1cfb",
    "url": "https://static.wixstatic.com/media/cd12f7_eb51af3990f146ec8b5f1fe3ad9d258f~mv2.jpg",
    "title": "Lucid air full body stain PPF ",
    "description": ""
  },
  {
    "id": "bb3082cf-7fbd-4dee-aadc-78ab5e1f5d53",
    "url": "https://static.wixstatic.com/media/cd12f7_c3aeff6dd7354210a05b0e27ae384060~mv2.jpg",
    "title": "Lucid air getting full body satin PPF ",
    "description": ""
  },
  {
    "id": "7da7b77d-04bf-41d7-bf4c-5fa17422dbfe",
    "url": "https://static.wixstatic.com/media/cd12f7_3637db875a41440283e1d561bc3f6ef5~mv2.jpg",
    "title": "lamborghini",
    "description": "2 face wrap on this lamborghini"
  },
  {
    "id": "7f000dda-f735-4b44-8fbb-dd7e3b13d219",
    "url": "https://static.wixstatic.com/media/cd12f7_3a1b13c5916546b1b43adaceab1d84c6~mv2.jpg",
    "title": "mazda 3/ e46 bmw m3",
    "description": "mazda 3 tinted 30% windscreen/ satin purple vinyl wrap on bmw windscreen 70%"
  },
  {
    "id": "7a188ee0-9679-4e52-a48f-4a670dd1cad9",
    "url": "https://static.wixstatic.com/media/cd12f7_a5bf8e84444c464c998ec385269b1679~mv2.png",
    "title": "lamborghini",
    "description": "15% sides and rear ceramic tint, full front ppf "
  },
  {
    "id": "d8566bfe-9eb1-46ca-919b-cec249a03934",
    "url": "https://static.wixstatic.com/media/cd12f7_f97bfa9ae9e04544a7a7346ade147530~mv2.png",
    "title": "lamborghini",
    "description": "top down getting ready for tint"
  },
  {
    "id": "0640294b-ba9e-4c14-8a5d-4d5385c723c0",
    "url": "https://static.wixstatic.com/media/cd12f7_8065084f1f6c487facb76496f48ed204~mv2.png",
    "title": "lamborghini",
    "description": "showing off the goods tinting it "
  },
  {
    "id": "157c9744-a1dc-4dbd-b441-ee5b87c3c844",
    "url": "https://static.wixstatic.com/media/cd12f7_e70710a521704fcd96033be4bb201bc2~mv2.png",
    "title": "bmw",
    "description": ""
  },
  {
    "id": "ec16bc09-b92b-43f9-aad4-1da5ed317116",
    "url": "https://static.wixstatic.com/media/cd12f7_8f8b5f8d537d4dd7a498826b4f6ba3ee~mv2.png",
    "title": "bmw ",
    "description": "tinted this 20%"
  },
  {
    "id": "6f888b01-e684-4fbc-9ef1-a98c7c80ab1c",
    "url": "https://static.wixstatic.com/media/cd12f7_5f01f411afeb4aa0a01d7f8fc76c3c57~mv2.png",
    "title": "bmw ",
    "description": "before tint"
  },
  {
    "id": "2bb9dc8b-4ee5-45f0-972f-5fd03307defc",
    "url": "https://static.wixstatic.com/media/cd12f7_7338d91dd07c4db6857d3e67ccc9a52b~mv2.png",
    "title": "mustang ev",
    "description": "full front end ppf and tint "
  },
  {
    "id": "2a9751dc-b55d-49d4-a143-3f35e8200da8",
    "url": "https://static.wixstatic.com/media/cd12f7_e797dcd6990341819d52593aeea72ad8~mv2.png",
    "title": "cadillac ct5 v ",
    "description": "before tint"
  },
  {
    "id": "c705a119-a41d-4d31-b6eb-8a39897fdf6a",
    "url": "https://static.wixstatic.com/media/cd12f7_a7fa75357d454eeb85bc914f80094fe3~mv2.png",
    "title": "mustang ev ",
    "description": "tinted 20% "
  },
  {
    "id": "e8aa9761-4ac0-4aa7-8d4e-9e92779384cb",
    "url": "https://static.wixstatic.com/media/cd12f7_6f410d0678864218824c1e8ec7510ab1~mv2.png",
    "title": "IMG_1478.HEIC",
    "description": ""
  },
  {
    "id": "da9876b4-41fe-4120-87a7-6f6d5f3fb3e0",
    "url": "https://static.wixstatic.com/media/cd12f7_de62ab1f4dc54dd895f4f1fc1b291d23~mv2.png",
    "title": "IMG_1476.HEIC",
    "description": ""
  },
  {
    "id": "5e21c342-606f-4a62-85fc-58fffdaf3943",
    "url": "https://static.wixstatic.com/media/cd12f7_a5e883891616409c94d244742e5b9bfc~mv2.png",
    "title": "IMG_1474.HEIC",
    "description": ""
  },
  {
    "id": "a88ef353-c872-4037-bbf2-952b14631aa4",
    "url": "https://static.wixstatic.com/media/cd12f7_c3ed75854b194003a2687f60de43ac4c~mv2.png",
    "title": "IMG_1469.HEIC",
    "description": ""
  },
  {
    "id": "c32e0f9d-f9a1-4b20-8ff5-697902ecdbe5",
    "url": "https://static.wixstatic.com/media/cd12f7_86051b5318a5413d89cc9441114e13ba~mv2.png",
    "title": "IMG_1460.HEIC",
    "description": ""
  },
  {
    "id": "d1f3376b-9645-4c8f-9afd-189656e087f1",
    "url": "https://static.wixstatic.com/media/cd12f7_a7ffb1938eef466d98142b195c9891aa~mv2.png",
    "title": "IMG_1459.HEIC",
    "description": ""
  },
  {
    "id": "8c6e05d4-3fed-4c4b-ac50-561bd9e7c0fc",
    "url": "https://static.wixstatic.com/media/cd12f7_93cd9b50517649ef9228baba0f0e1cd9~mv2.png",
    "title": "IMG_1448.HEIC",
    "description": ""
  },
  {
    "id": "b5c70474-4822-40fe-a3f3-340191e74507",
    "url": "https://static.wixstatic.com/media/cd12f7_5002b16b8c4648409019aecf57109666~mv2.png",
    "title": "IMG_1445.HEIC",
    "description": ""
  },
  {
    "id": "5ae9dc95-f98c-423c-ad82-7b3ac034e0cf",
    "url": "https://static.wixstatic.com/media/cd12f7_b544cf833e9448c2bb58a280c58262e4~mv2.png",
    "title": "IMG_1442.HEIC",
    "description": ""
  },
  {
    "id": "adc71b16-39d8-49ab-b7f5-931edbd6e441",
    "url": "https://static.wixstatic.com/media/cd12f7_9a9a3b6766c04afdadfee9cf2ee370a8~mv2.png",
    "title": "IMG_1435.HEIC",
    "description": ""
  },
  {
    "id": "bc1119c7-975f-42fa-a6e3-134f88761475",
    "url": "https://static.wixstatic.com/media/cd12f7_7ebe5f461e39448fab803111085b6eb0~mv2.png",
    "title": "IMG_1434.HEIC",
    "description": ""
  },
  {
    "id": "bafd1831-044e-4d1d-871b-99799fea573c",
    "url": "https://static.wixstatic.com/media/cd12f7_74fe7196a4a8406284adae22de1d0d0c~mv2.jpg",
    "title": "IMG_1409.jpg",
    "description": ""
  },
  {
    "id": "10bbc638-47d0-438d-afd7-bafc092814f2",
    "url": "https://static.wixstatic.com/media/cd12f7_eef99abc246446bdac33e6b5051d6e63~mv2.png",
    "title": "IMG_1406.HEIC",
    "description": ""
  },
  {
    "id": "4f294344-deda-4989-bba4-1e578f19897d",
    "url": "https://static.wixstatic.com/media/cd12f7_9e5c7e9372964e24b7b4f5dad89c2ba7~mv2.png",
    "title": "IMG_1405.HEIC",
    "description": ""
  },
  {
    "id": "fd21c832-7d95-4cdc-ad00-162db4d3b9e7",
    "url": "https://static.wixstatic.com/media/cd12f7_97477f4450a44225bc6755eac6fbe978~mv2.png",
    "title": "IMG_1401.HEIC",
    "description": ""
  },
  {
    "id": "819e8f32-23cd-41ca-a03c-bb21462a68a1",
    "url": "https://static.wixstatic.com/media/cd12f7_d8dd8f86f4f34063b205175758ebdef0~mv2.png",
    "title": "IMG_1400.HEIC",
    "description": ""
  },
  {
    "id": "d4c97280-3bbc-4adc-8076-733a627f4472",
    "url": "https://static.wixstatic.com/media/cd12f7_77fa3985fb4e4e7d997b4643411f3cb5~mv2.png",
    "title": "IMG_1399.HEIC",
    "description": ""
  },
  {
    "id": "ef69b888-f4df-488c-9293-70f88cd51e2a",
    "url": "https://static.wixstatic.com/media/cd12f7_962cda73d56d4665858530f259c56a31~mv2.png",
    "title": "IMG_1397.HEIC",
    "description": ""
  },
  {
    "id": "c4942afe-ff43-4309-8c96-46d77088f606",
    "url": "https://static.wixstatic.com/media/cd12f7_3c5f89a0ad0244ec8b0459ce7ec0f633~mv2.png",
    "title": "IMG_1384.HEIC",
    "description": ""
  },
  {
    "id": "293deb08-6902-49f7-8f36-0129a721a38a",
    "url": "https://static.wixstatic.com/media/cd12f7_49f0b1044350431a9625042abde4368d~mv2.png",
    "title": "IMG_1383.HEIC",
    "description": ""
  },
  {
    "id": "6936d988-9e78-4938-bac5-e32c08a408b7",
    "url": "https://static.wixstatic.com/media/cd12f7_c7312781acb346cdb73c19fb8ba92f0c~mv2.png",
    "title": "IMG_1382.HEIC",
    "description": ""
  },
  {
    "id": "bf7fbc81-959b-47f2-a1c0-2919d72a3a10",
    "url": "https://static.wixstatic.com/media/cd12f7_cda61b1765d24e7a80ec95a7d7ea23c2~mv2.png",
    "title": "IMG_1381.HEIC",
    "description": ""
  },
  {
    "id": "d5e5fdc0-2441-48ae-abd9-63b56811691c",
    "url": "https://static.wixstatic.com/media/cd12f7_e2f968b6e46c4cbc9e7eb1f8f4239180~mv2.png",
    "title": "IMG_1366.HEIC",
    "description": ""
  },
  {
    "id": "b6812e65-f762-47c6-90c5-045100a24f48",
    "url": "https://static.wixstatic.com/media/cd12f7_96f3d52fa722466c8ac5de6625e9cfc0~mv2.png",
    "title": "IMG_1364.HEIC",
    "description": ""
  },
  {
    "id": "8bce6a05-5084-4518-b8b5-3483aa8feea4",
    "url": "https://static.wixstatic.com/media/cd12f7_7f6e7cb24a114c30821eb3e96b9f503b~mv2.png",
    "title": "IMG_1346.HEIC",
    "description": ""
  },
  {
    "id": "f90fc03e-2afd-4cae-a7d0-57acaa3a7697",
    "url": "https://static.wixstatic.com/media/cd12f7_e44702d001564c33ac2ca6deaebd1960~mv2.jpg",
    "title": "IMG_1339.jpg",
    "description": ""
  },
  {
    "id": "f5689c3c-e978-4e30-8b98-816d14bee09f",
    "url": "https://static.wixstatic.com/media/cd12f7_639c7b56876d46e3aff6a117f9d06a17~mv2.jpg",
    "title": "IMG_1339.jpg",
    "description": ""
  },
  {
    "id": "7ef7e246-0abe-4f86-83aa-1e78741608dc",
    "url": "https://static.wixstatic.com/media/cd12f7_3c7a0f6479c74d8c8836791cbf24dbff~mv2.png",
    "title": "IMG_1338.HEIC",
    "description": ""
  },
  {
    "id": "16941130-8c21-493b-a791-861339481d05",
    "url": "https://static.wixstatic.com/media/cd12f7_771d2a7227484ea28fc219cc73cfb500~mv2.png",
    "title": "IMG_1207.jpg",
    "description": ""
  },
  {
    "id": "d69575d9-4306-46c6-bfd1-e7e44375d668",
    "url": "https://static.wixstatic.com/media/cd12f7_9bde2127f3ce46cf88c417fd4fd60bc3~mv2.png",
    "title": "2021 Tesla model y",
    "description": "Ceramic coating 3m ceramic coating "
  },
  {
    "id": "726c9487-226b-4f04-a788-6f2ed687829d",
    "url": "https://static.wixstatic.com/media/cd12f7_67df7ba88c974a55b2e2503c4f17030d~mv2.png",
    "title": "2017 Range Rover ",
    "description": "3M matte dead black vinyl wrap"
  },
  {
    "id": "b5ce60bf-f00b-46be-900b-12415064b9d9",
    "url": "https://static.wixstatic.com/media/cd12f7_39a3ab4ee47d47b3bc622e032613fbc1~mv2.png",
    "title": "2017 Range Rover ",
    "description": "Tinted windshield along with 3m matte dead black "
  },
  {
    "id": "297027fb-1372-4d70-acbf-2d9b7ef862e1",
    "url": "https://static.wixstatic.com/media/cd12f7_d4dbdfbef7584ec1918f82fa81baf7eb~mv2.png",
    "title": "2017 Range Rover ",
    "description": "Full matte wrap and blac badges "
  },
  {
    "id": "3b11026f-835d-4d2d-a1f2-2a37e38c973b",
    "url": "https://static.wixstatic.com/media/cd12f7_d43f9fd4717243e98b052995aaac552e~mv2.png",
    "title": "IMG_1191.HEIC",
    "description": ""
  },
  {
    "id": "fefd846f-2681-4d65-af43-e42fced82cd8",
    "url": "https://static.wixstatic.com/media/cd12f7_bbf5f698ca68411fbab75708cdd6e9a6~mv2.png",
    "title": "2021 xc90",
    "description": "Full ceramic coating "
  },
  {
    "id": "f66469a9-a274-443b-98ca-197053a81b7d",
    "url": "https://static.wixstatic.com/media/cd12f7_64ad02ba38584985b4380b2fd4a8bd39~mv2.png",
    "title": "2021 xc90",
    "description": "The process before we ceramic coat "
  },
  {
    "id": "6c7bed22-da81-4290-a85f-cad9d9beba42",
    "url": "https://static.wixstatic.com/media/cd12f7_585d055f34bc441b9aedfe302b6f0859~mv2.png",
    "title": "IMG_1166.HEIC",
    "description": ""
  },
  {
    "id": "48f4d7dd-36d0-4b9d-8746-7937bf7ac8da",
    "url": "https://static.wixstatic.com/media/cd12f7_214a5a4bfcd6424a8aa0ac0b900f54ed~mv2.png",
    "title": "2022 bmw z4",
    "description": "Factory satin paint job we did paint protection (ppf)"
  },
  {
    "id": "5bc56566-2000-4335-815a-84a06ee2884e",
    "url": "https://static.wixstatic.com/media/cd12f7_993ca21781424045a52ab170f5d82565~mv2.png",
    "title": "IMG_1161.HEIC",
    "description": ""
  },
  {
    "id": "4ac581b5-d9ee-43ce-b167-ea60fbc86314",
    "url": "https://static.wixstatic.com/media/cd12f7_f7f3a1dcd2324ceab4c408ccfc294b94~mv2.png",
    "title": "2018 jaguar xe",
    "description": "Tinted the taillights 20%"
  },
  {
    "id": "c5cc9a9a-4f45-4d24-a801-e06dedf1ed99",
    "url": "https://static.wixstatic.com/media/cd12f7_4a9308f4eec74425bce92fa30eb67e67~mv2.png",
    "title": "2018 jaguar xe",
    "description": "The process before we tint taillights "
  },
  {
    "id": "4f22e7ec-a743-4624-aecb-ef9c5439a385",
    "url": "https://static.wixstatic.com/media/cd12f7_b114cd09106e4376a3e6a7831af9187d~mv2.png",
    "title": "IMG_1149.HEIC",
    "description": ""
  },
  {
    "id": "bd68f6f1-2b7e-46b4-b6f0-b54c1c03a696",
    "url": "https://static.wixstatic.com/media/cd12f7_0ecf6f36bc8a4f9b92e950893e0aa203~mv2.png",
    "title": "2017 Frs ",
    "description": "My edges when I lay clear bra /paint protection film (ppf)"
  },
  {
    "id": "5dda4977-913f-4490-93d6-3ffbe5185ee7",
    "url": "https://static.wixstatic.com/media/cd12f7_e8ea144af8004d7b91f0a091b5c55fe0~mv2.png",
    "title": "2021 Tesla model y",
    "description": "Looking fancy with my rear plate decal and new tint along with 3m ceramic coating "
  },
  {
    "id": "2e539628-f6e0-4547-acef-a454951f3270",
    "url": "https://static.wixstatic.com/media/cd12f7_f6145be980fb4eae9bd10a85d0209116~mv2.jpg",
    "title": "mazda b2200",
    "description": "getting spicy with the mini truck"
  },
  {
    "id": "e92db970-a9ea-48ed-808a-d4cb2ca15af2",
    "url": "https://static.wixstatic.com/media/cd12f7_f80ee538411d49e6804cf28c8819c1bc~mv2.png",
    "title": "range rover lummis",
    "description": "custom range rover 5% tint "
  },
  {
    "id": "d5880d6b-6f05-4433-9407-c76bac3e329f",
    "url": "https://static.wixstatic.com/media/cd12f7_329fe77e3ec64565905092a085f3415d~mv2.png",
    "title": "2021 RSQ8",
    "description": "full 3M crystalline tint 30% front doors 90% windshield 60% over factory rear for 97% heat rejection "
  },
  {
    "id": "b09d5e16-ffca-49ad-bde3-15989cd43d94",
    "url": "https://static.wixstatic.com/media/cd12f7_d34fde5415c14edb8c550ee7c34f2b56~mv2.jpg",
    "title": "bmw i3",
    "description": "i think kris is happy with himself today cars clean and ready to give back to client "
  },
  {
    "id": "0a29dbfc-b5b4-44ce-9513-7e474818188a",
    "url": "https://static.wixstatic.com/media/cd12f7_ce12a417d6a64e9eb47c5ba9fc59e16c~mv2.jpg",
    "title": "bmw i3",
    "description": "very shiny after the major work we did today"
  },
  {
    "id": "3d40a052-86ad-4a17-a5ad-78e4c167de86",
    "url": "https://static.wixstatic.com/media/cd12f7_13aed94e66b7461ab124714a874e9adc~mv2.jpg",
    "title": "bmw i3",
    "description": "full tint 25% 50% windshield full clear bra/PPF (paint protection film) entire car clear plex on windshield and ceramic coating "
  },
  {
    "id": "b42a5834-4862-441c-b776-76661e7880cd",
    "url": "https://static.wixstatic.com/media/cd12f7_160e158dab73442d9ce1fcc627cc8e63~mv2.png",
    "title": "dodge durango",
    "description": "clear bra/PPF (paint protection film) front end"
  },
  {
    "id": "5aa292fd-179f-4a73-b064-2ec034f2bf04",
    "url": "https://static.wixstatic.com/media/cd12f7_4af7383467eb4078bdb4056b517cb2b5~mv2.png",
    "title": "2021 dodge charger hellcat",
    "description": "3M clear PPF (paint protection film) installed, satin black on hood roof and spoiler, and 3M SATIN ppf installed on those black pieces keeping them with a satin finish"
  },
  {
    "id": "52a1400e-fc1b-4aed-95e4-7b1cb13254b2",
    "url": "https://static.wixstatic.com/media/cd12f7_484ebc9956be479e885860b46577cdc6~mv2.png",
    "title": "audi a4",
    "description": "taillight tint "
  },
  {
    "id": "16636409-acfd-404f-9f5b-ce3ef9965022",
    "url": "https://static.wixstatic.com/media/cd12f7_4e00c0d64b1d45318e02beda71c956d2~mv2.png",
    "title": "tesla model Y",
    "description": "matte blue metallic vinyl wrap 3M"
  },
  {
    "id": "f9c16053-8c90-4832-8969-cfc2e6c1756f",
    "url": "https://static.wixstatic.com/media/cd12f7_7393761cf35f4cb492d6882ff25c4965~mv2.png",
    "title": "tesla model Y",
    "description": "full color change 3M vinyl wrap matte metallic blue wrap"
  },
  {
    "id": "0e5d3358-fd7f-472e-85bd-922e237f3c68",
    "url": "https://static.wixstatic.com/media/cd12f7_d2c718538bee45e68ba18aa775d6b3d5~mv2.png",
    "title": "outlaw catamaran",
    "description": "paint correction and ceramic coating installed "
  },
  {
    "id": "fd471332-734d-4ca4-bb89-5d8ebd307f84",
    "url": "https://static.wixstatic.com/media/cd12f7_371abaf0963a470e8703002610b29f1a~mv2.png",
    "title": "sport chassis",
    "description": "full clear bra/PPF (paint protection film)"
  },
  {
    "id": "3e349f15-5ca8-4fb8-9d71-fd259949e32d",
    "url": "https://static.wixstatic.com/media/cd12f7_bee56c5fdd30462d8ad51b16be66a57d~mv2.png",
    "title": "2020 c8 corvette ",
    "description": "full clear bra/PPF (paint protection film) and gloss black roof"
  },
  {
    "id": "dcf39728-760f-4c54-9889-8d1e8ab610ed",
    "url": "https://static.wixstatic.com/media/cd12f7_69c53123853d48839b58e0481edad4e6~mv2.jpg",
    "title": "",
    "description": ""
  },
  {
    "id": "67b50a07-41f5-410a-a088-698f97a3b3cf",
    "url": "https://static.wixstatic.com/media/cd12f7_69c53123853d48839b58e0481edad4e6~mv2.jpg",
    "title": "",
    "description": ""
  },
  {
    "id": "97476b37-2bca-405d-9885-bd3df17987ee",
    "url": "https://static.wixstatic.com/media/cd12f7_fe5a25fd981948bf801c9d4f5353bc7d~mv2.jpg",
    "title": "",
    "description": ""
  },
  {
    "id": "aab734a1-1546-43c8-8568-d7fd248d04b6",
    "url": "https://static.wixstatic.com/media/cd12f7_fc48f12f313e4651bbd94a09b95e90d4~mv2.jpg",
    "title": "",
    "description": ""
  },
  {
    "id": "1972916b-fe25-4823-9cd5-ad832bb8912d",
    "url": "https://static.wixstatic.com/media/cd12f7_dc481df17fbf44e0a559a31e14f7bcd8~mv2.jpg",
    "title": "2020 type R",
    "description": "reflective vinyl "
  },
  {
    "id": "554340b2-a825-41fe-9df3-1c23a8379fde",
    "url": "https://static.wixstatic.com/media/cd12f7_349658eef11246c8b99a0809826e7767~mv2.jpg",
    "title": "2020 civic type R",
    "description": "black reflective vinyl "
  },
  {
    "id": "540f8226-1941-4886-b103-b878bfd6067a",
    "url": "https://static.wixstatic.com/media/cd12f7_6fec96cdc88a463dbc0826a73e3f6d10~mv2.jpg",
    "title": "2012 springdale",
    "description": "camping trailer window tint 35%"
  },
  {
    "id": "d0f9167a-dc0f-4cab-b8d3-395a02e77187",
    "url": "https://static.wixstatic.com/media/cd12f7_8a98b15fb05344088ffb102df55b3fcc~mv2.jpg",
    "title": "2020 corvette c7",
    "description": "tailight tint full clear bra/ PPF (paint protection film) full vehicle "
  },
  {
    "id": "ba76ac21-c6f2-4f27-ad47-f46ba2bd0330",
    "url": "https://static.wixstatic.com/media/cd12f7_141f3d17afcd48eb921fb75cc4cab496~mv2.jpg",
    "title": "2017 mazda 3",
    "description": "full front end clear bra/ PPF ( paint protection film)"
  },
  {
    "id": "9174b6cf-3c20-4cc9-971d-df632aed9316",
    "url": "https://static.wixstatic.com/media/cd12f7_aa0a9b8819224da0826b7664dd979bb0~mv2.jpg",
    "title": "toyota frs ",
    "description": "color change key west vinyl over the factory yellow "
  },
  {
    "id": "ef9dcaf8-bf49-40dc-bb0c-7006539ebd15",
    "url": "https://static.wixstatic.com/media/cd12f7_ba808d9da30c42f7bb3093f985993251~mv2.jpg",
    "title": "IMG_0152.jpg",
    "description": ""
  },
  {
    "id": "91dbd91f-a306-4552-a97c-fcf12e2d00f8",
    "url": "https://static.wixstatic.com/media/cd12f7_acec106b7592416fa512a5a80152c3ec~mv2.jpg",
    "title": "IMG_0114.jpg",
    "description": ""
  },
  {
    "id": "aabf4a1e-586a-47cc-888d-7faf7207c3b3",
    "url": "https://static.wixstatic.com/media/cd12f7_c0fdaa59639b479aae4f596ad0072d9c~mv2.jpg",
    "title": "IMG_0112.jpg",
    "description": ""
  },
  {
    "id": "40cfe34b-d3ca-4898-9a0c-4d668e2d8e60",
    "url": "https://static.wixstatic.com/media/cd12f7_8a5f60f5837f4c67b769fac3f013463a~mv2.jpg",
    "title": "porsche",
    "description": "clear bra/ PPF (paint protection film)"
  },
  {
    "id": "48a3ea8f-6b04-47a9-884c-ada001ec2bac",
    "url": "https://static.wixstatic.com/media/cd12f7_71f69ac24c394fc3aa00821592687abb~mv2.jpg",
    "title": "porsche",
    "description": "clear bra/ PPF (paint protection film)"
  },
  {
    "id": "1ca7deda-1cc1-45e7-bdbe-46a2629b6fbd",
    "url": "https://static.wixstatic.com/media/cd12f7_77b21cdcdcc84ae28aa915e303d04c32~mv2.jpg",
    "title": "porsche",
    "description": "plotted kit of the clear bra/PPF  (paint protection film) weeding oout the kit for optimal install"
  },
  {
    "id": "68de73bd-3bf5-43d0-851c-f006b7e2c166",
    "url": "https://static.wixstatic.com/media/cd12f7_82e173229b68425198483a01cdbdc6ec~mv2.jpg",
    "title": "kenworth",
    "description": "big rig tint "
  },
  {
    "id": "48854118-2b97-4b5c-95e3-7faa463756d9",
    "url": "https://static.wixstatic.com/media/cd12f7_c45b9b266b444376a00eeb4cec0b13ae~mv2.jpg",
    "title": "g63 amg",
    "description": "headlight protection"
  },
  {
    "id": "aac6750a-58ef-4445-9716-f6c92891896c",
    "url": "https://static.wixstatic.com/media/cd12f7_0bcf724efb9f466593d75559f5eb6040~mv2.jpg",
    "title": "jeep wrangler",
    "description": "satin black accents on jeep wrangler hand layed/ hand cut"
  },
  {
    "id": "811e4007-b0a8-4517-afcb-1446d755bd70",
    "url": "https://static.wixstatic.com/media/cd12f7_565b912857494e588aa7f982f8ddb425~mv2.jpg",
    "title": "dodge viper",
    "description": "full tint 35%"
  },
  {
    "id": "5a49bb05-23e5-4b23-a8eb-4eb863f6ccd3",
    "url": "https://static.wixstatic.com/media/cd12f7_a2766c1f7b5c4c9f99a503e3a3017cb8~mv2.jpg",
    "title": "van",
    "description": "this 1 ton swapped van installing 3 piece AMERICAN flag install in vinyl"
  },
  {
    "id": "fdacb37b-9c1c-4d14-a0e8-82235e5429e8",
    "url": "https://static.wixstatic.com/media/cd12f7_6bcddb0f55e94c838a0c71e9e586d566~mv2.jpg",
    "title": "2012 mazda 3",
    "description": "headlight tint in chameleon "
  },
  {
    "id": "2a83b3b5-3b18-49e2-8f1d-6766964f0405",
    "url": "https://static.wixstatic.com/media/cd12f7_8c1ae1472bf3487e91fab9d1b617d424~mv2.jpg",
    "title": "IMG_0085.HEIC",
    "description": ""
  },
  {
    "id": "b1c46a09-588e-4f65-88ab-0c0426239541",
    "url": "https://static.wixstatic.com/media/cd12f7_e04373a5951a4b80b7e80bc4374d4460~mv2.jpg",
    "title": "2012 mazda 3 ",
    "description": "HID headlight installation after chameleon wrap installed"
  },
  {
    "id": "485ded7b-4aad-4029-b541-ae5f151350a4",
    "url": "https://static.wixstatic.com/media/cd12f7_41709ded8e0642648c32aa179ab0c428~mv2.jpg",
    "title": "2020 dodge viper ACR",
    "description": "full front end clear bra/ PPF (paint protection film) custom hand cut around the stripes "
  },
  {
    "id": "54a343ad-f6d7-4d2d-a64b-aef14426cc9f",
    "url": "https://static.wixstatic.com/media/cd12f7_b40ca65a284140099da52881d982abae~mv2.jpg",
    "title": "dodge viper acr",
    "description": "full pic of the hood getting installed in clear bra/PPF (paint protection film)"
  },
  {
    "id": "f9ad0f96-a9f4-46f9-a4cb-c3a840534597",
    "url": "https://static.wixstatic.com/media/cd12f7_5de178cc16b24a23b1961e9be9d85294~mv2.jpg",
    "title": "ferrari f430",
    "description": "bumper clear bra/PPF (paint protection film) install"
  },
  {
    "id": "690e4c1e-000d-44dd-aaf0-71882deb45b3",
    "url": "https://static.wixstatic.com/media/cd12f7_52e50498aac547b9a7bcb4ec36a0b35a~mv2.jpg",
    "title": "IMG_0081.JPEG",
    "description": ""
  },
  {
    "id": "39dc5c35-5838-45a2-8728-b2aa01c70887",
    "url": "https://static.wixstatic.com/media/cd12f7_1c036257c23449289e17b712053f59aa~mv2.jpg",
    "title": "mazerati ",
    "description": "full front end clear bra/ PPF (paint protection film) wrapped edges"
  },
  {
    "id": "70478933-7fe6-4b3b-976c-3b2ca31e7653",
    "url": "https://static.wixstatic.com/media/cd12f7_f610b45f38e143f894c3ae20205b94a9~mv2.jpg",
    "title": "mazerati",
    "description": "streteching the clear bra/PPF (paint protection film) to pull all tension out of it then squeegee all solution out"
  },
  {
    "id": "c170a019-d23b-4a36-b4ee-272f7f1e8761",
    "url": "https://static.wixstatic.com/media/cd12f7_2d60ecec6e0c40da9f06ca394df5b124~mv2.jpg",
    "title": "merecedes gl",
    "description": "before we trim the clear bra/PPF (paint protection film)"
  },
  {
    "id": "40e4fa1a-e6e3-44c8-a1ab-94526cac8751",
    "url": "https://static.wixstatic.com/media/cd12f7_89d39fc39c7248949ad9e225778245e5~mv2.jpg",
    "title": "mercedes gl",
    "description": "making sure everythings fully covered with paint protection film (ppf)"
  },
  {
    "id": "b66eb841-35e3-4295-bc64-07546b675238",
    "url": "https://static.wixstatic.com/media/cd12f7_11b08044500b4312bd1f9bffaedc7104~mv2.jpg",
    "title": "mazerati ghibli",
    "description": "full front end clear bra/PPF ( paint protection film)"
  },
  {
    "id": "94ab7ffc-0f55-42f4-b6a7-abd19c9da19c",
    "url": "https://static.wixstatic.com/media/cd12f7_ad8d20a252e04b5aa28cf591221e7144~mv2.jpg",
    "title": "2 tesla model 3 ",
    "description": "tinting both cars back to back"
  },
  {
    "id": "7b7e4c0a-97ca-4e69-bc60-edbeee882ce4",
    "url": "https://static.wixstatic.com/media/cd12f7_91045c1c5b554f75b9d7cd5b8507fc86~mv2.jpg",
    "title": "3 teslas ",
    "description": "tint on all cars and clear bra/PPF (paint protection film) full body wraps as well"
  },
  {
    "id": "ab63448f-441c-4021-a3a7-55c24f3c870d",
    "url": "https://static.wixstatic.com/media/cd12f7_5af87753d7a549f095cba3408a8c03a0~mv2.jpg",
    "title": "toyota 4runner ",
    "description": "5% tint all around "
  },
  {
    "id": "7db82ad8-8b2a-4479-a3ce-77d4bc658189",
    "url": "https://static.wixstatic.com/media/cd12f7_3fe4748c51964892a832cc55b7639680~mv2.jpg",
    "title": "mazda b2200",
    "description": "tinting back glass of mazda b2200"
  },
  {
    "id": "177bcfb7-f943-4525-98d8-208ce156d964",
    "url": "https://static.wixstatic.com/media/cd12f7_3e9e921478db40a991131fada87e3f63~mv2.jpg",
    "title": "tesla model x",
    "description": "tinting to match 20%"
  },
  {
    "id": "a868d964-b65c-4b3b-942e-e03182d48832",
    "url": "https://static.wixstatic.com/media/cd12f7_c12f41956dee44c0a121a2865a627954~mv2.png",
    "title": "gl450 and c300",
    "description": "both cars getting tint"
  },
  {
    "id": "e35280e4-0336-4a4e-96ed-558ce9f6f739",
    "url": "https://static.wixstatic.com/media/cd12f7_da06ac0d36124cb9b639c6c4e01fc6f7~mv2.jpg",
    "title": "bmw i3",
    "description": "the start of the installs for kris today"
  },
  {
    "id": "4e665752-9962-4250-98fb-ad533fb45e2c",
    "url": "https://static.wixstatic.com/media/cd12f7_f39476a06fc9458d8f0d8a8fc6111775~mv2.jpg",
    "title": "honda civic",
    "description": "headlight tint done"
  },
  {
    "id": "b6098658-088c-4c9b-bb89-0ff8c98b0b63",
    "url": "https://static.wixstatic.com/media/cd12f7_de06c114a50f4e7187e9e40d614c0148~mv2.jpg",
    "title": "honda civic",
    "description": "taillight tint precision is key"
  },
  {
    "id": "cafbff8c-3e58-4ee4-bb59-48da4a9842fd",
    "url": "https://static.wixstatic.com/media/cd12f7_5697755a0e4647529f093c56ceae1fa6~mv2.jpg",
    "title": "bmw 6 series",
    "description": "25% tint on sides and 50% windshield"
  },
  {
    "id": "03170380-d0f0-431e-b66b-55f01032ec58",
    "url": "https://static.wixstatic.com/media/cd12f7_4349a659cbf4420baf1dec331812eb15~mv2.jpg",
    "title": "jeep trackhawk",
    "description": "overview before we install second stripe"
  },
  {
    "id": "470c06b4-e3d2-4a10-bcea-9bf6178f7321",
    "url": "https://static.wixstatic.com/media/cd12f7_daa541c3c4584ca4a3b4d373d5569b24~mv2.jpg",
    "title": "jeep trackhawk",
    "description": "kris very precisely cutting and finishing the first install of 2 stripes"
  },
  {
    "id": "0f798f61-ea34-4c58-8801-f4f07183e2f9",
    "url": "https://static.wixstatic.com/media/cd12f7_a6d7ddf3319440869ec46b05eba8107a~mv2.jpg",
    "title": "2020 jeep grand cherokee trackhawk",
    "description": "hand laying 3M vinyl carbon fiber stripes on the vehicle with knifeless tape and hand cutting"
  },
  {
    "id": "07a2d2b5-bde7-4868-b961-cc795239de37",
    "url": "https://static.wixstatic.com/media/cd12f7_e834f1030638424297632d4084800d99~mv2.jpg",
    "title": "tesla model 3",
    "description": "kris installing full front end clear bra/PPF (paint protection film) "
  },
  {
    "id": "8aa1e5ad-c41b-4646-bc2e-5a9e7fd00cb6",
    "url": "https://static.wixstatic.com/media/cd12f7_c0f0f16982a8400c8fcb17ec634e3097~mv2.jpg",
    "title": "ford raptor",
    "description": "hood piece is layed now trim and wrap edges for finished product"
  },
  {
    "id": "73701576-56f2-419b-a932-aa2ec0443f62",
    "url": "https://static.wixstatic.com/media/cd12f7_2d510a2f40374e7db87f0c812f86be3f~mv2.jpg",
    "title": "ford raptor ",
    "description": "full 3m clear bra/ PPF (paint protection film) on front end "
  },
  {
    "id": "c4cd192d-9d6e-4e9b-8cff-0ef2e1f69dd3",
    "url": "https://static.wixstatic.com/media/cd12f7_d443e78e7ce14a5e89985a3429878676~mv2.jpg",
    "title": "ford raptor",
    "description": "the beginnning stages of install getting clear bra/PPF (paint protection film) on the vehicle"
  },
  {
    "id": "52585d97-ecde-47a0-bdac-dc9de3e4cbf8",
    "url": "https://static.wixstatic.com/media/cd12f7_ed88b1b4d5b94ec3bfe5a4f4e4fde397~mv2.jpg",
    "title": "ford raptor",
    "description": "kris (installer) mocking the clear bra/ PPF (paint protection film) on the vehicle"
  },
  {
    "id": "2cfac348-4e99-4609-8018-6c02ea7ce6dc",
    "url": "https://static.wixstatic.com/media/cd12f7_56f1c6bf296a440c853dc270b918b7d1~mv2.jpg",
    "title": "bmw tesla and ferrari ",
    "description": "busy day with alot of cars "
  },
  {
    "id": "ad320feb-5d49-46a9-9ac4-1c15ccd9d066",
    "url": "https://static.wixstatic.com/media/cd12f7_7be5cf480d7c49d0ae95c2dfdb3b330e~mv2.jpg",
    "title": "chevy camaro",
    "description": "pink badges wrapped pink stripes we made installed its ready for the road"
  },
  {
    "id": "da7353bc-1320-4080-98c1-3e0daac786f7",
    "url": "https://static.wixstatic.com/media/cd12f7_805c90d01b664394935aff37142c3cec~mv2.jpg",
    "title": "chevy camaro",
    "description": "pink stripes install "
  },
  {
    "id": "d5da8db0-33eb-48ce-9989-77648c46681c",
    "url": "https://static.wixstatic.com/media/cd12f7_077a898d218944f0914543e28e411e94~mv2.jpg",
    "title": "chevy camaro",
    "description": "pink bezel wrapped"
  },
  {
    "id": "8dce4293-a0ab-4690-8ad0-179d5e1e6e64",
    "url": "https://static.wixstatic.com/media/cd12f7_5b1789c6acfb43899b3e1859e095fe63~mv2.jpg",
    "title": "chevy camaro",
    "description": "alot of pink interior wrap going on this camaro"
  },
  {
    "id": "609fa247-3404-4644-b3d0-899b277faaf3",
    "url": "https://static.wixstatic.com/media/cd12f7_c5456e4ce3d34924a560c136bd7bbd42~mv2.jpg",
    "title": "chevy camaro ",
    "description": "pink interior pieces installed 3m films vinyl"
  },
  {
    "id": "8b00d642-8b54-4953-a133-a50028d9e003",
    "url": "https://static.wixstatic.com/media/cd12f7_e662f2883a104044961a727d18b5fd00~mv2.jpg",
    "title": "2018 honda civic",
    "description": "15% tint"
  },
  {
    "id": "dc2c1cab-36b3-4624-8840-936f5ada1e41",
    "url": "https://static.wixstatic.com/media/cd12f7_c400af34c4964ece87ed658026b91d9b~mv2.jpg",
    "title": "dodge challenger",
    "description": "tinted 15% "
  },
  {
    "id": "52cd52a6-7a89-40ef-ae60-07661585df30",
    "url": "https://static.wixstatic.com/media/cd12f7_39318114296a4367aadf57bdadc69cb3~mv2.jpg",
    "title": "subaru",
    "description": "more installs clear bra/PPF (paint protection film) "
  },
  {
    "id": "8efa0350-4f71-4dc2-940f-2a7eec9ff1e9",
    "url": "https://static.wixstatic.com/media/cd12f7_da6fa5e18ea24094a08981c5d5daaca4~mv2.jpg",
    "title": "06 E46 M3 BMW",
    "description": "purple wrap installed on the bmw m3"
  },
  {
    "id": "a251bc65-6df5-4897-9ef0-3fa9c036e7f0",
    "url": "https://static.wixstatic.com/media/cd12f7_13a13deffae448a9a1425cbcc1eb1e1e~mv2.jpg",
    "title": "2018 subaru sti",
    "description": "the start of 3M clear bra/ PPF (paint protection film) and how we lay it in between those hard to stretch areas. "
  },
  {
    "id": "8a207468-39bf-46e7-b8a9-adaf1f28cca6",
    "url": "https://static.wixstatic.com/media/cd12f7_73e6e3f071ed4e2995fd23987ac8bd54~mv2.jpg",
    "title": "bmw m3 ",
    "description": "full avery dennison vinyl wrap installed and taillight reverse lights smoked this was a very clean install"
  },
  {
    "id": "d7ba6ea8-a6c4-43c8-b622-cf0d3f67e91f",
    "url": "https://static.wixstatic.com/media/cd12f7_3fa3e1c4762840b18c348375810c1e0f~mv2.jpg",
    "title": "lotus evora",
    "description": "15% tint"
  },
  {
    "id": "0a663e60-676b-4c29-8cdc-bda0f5a84586",
    "url": "https://static.wixstatic.com/media/cd12f7_340b1837e6df4753a44742385396b32a~mv2.jpg",
    "title": "2020 jeep grand cherokee",
    "description": "full custom bumper skid plate/ winch install supplied by cheif products based out of australia"
  },
  {
    "id": "6663b744-4695-4020-9927-2cc9eda3ff33",
    "url": "https://static.wixstatic.com/media/cd12f7_63c877f6baf44304b4843e38d7cb214c~mv2.jpg",
    "title": "ford f100",
    "description": "custom built ford f100 in for ceramic coating and tint "
  },
  {
    "id": "0ce8cfb8-a0bd-40b0-abc8-4a1afeddc3b2",
    "url": "https://static.wixstatic.com/media/cd12f7_8c98aa6ad2a04bd9b3ae2e962394fa47~mv2.jpg",
    "title": "SUPRA",
    "description": "yes its s soooopra and we are finishing the back glass "
  },
  {
    "id": "9893de3c-87cd-48d5-889c-dd76b65792c1",
    "url": "https://static.wixstatic.com/media/cd12f7_c03c33c1ca9449e8b5ad7444ca026363~mv2.jpg",
    "title": "audi s4",
    "description": "full tear down of audi s4 getting full color change 3M vinyl wrap installed"
  },
  {
    "id": "923f83a3-7c60-42fe-a7fa-36e055a61721",
    "url": "https://static.wixstatic.com/media/cd12f7_82f48be1777b43359138cb123615de35~mv2.jpg",
    "title": "audi a4",
    "description": "full 3M color change vinyl install from white to satin black "
  },
  {
    "id": "dd5d0300-939e-4b69-bf03-5ad4f0c339f9",
    "url": "https://static.wixstatic.com/media/cd12f7_48a65f6f450446c18cc13ea7267d7ed7~mv2.jpg",
    "title": "mgb",
    "description": "full tinted windshield 30% on this bad boy"
  },
  {
    "id": "f82ccb0d-9580-46c5-9cc1-6a258096783a",
    "url": "https://static.wixstatic.com/media/cd12f7_a6b2ffec32f64ff0923f959f9123beff~mv2.jpg",
    "title": "tahoe",
    "description": "more pics of the pink monster"
  },
  {
    "id": "5a084bbc-33ac-4809-b288-c5bcdac45048",
    "url": "https://static.wixstatic.com/media/cd12f7_043c4ddbf2464ab18542e0f4ef3ccc1f~mv2.jpg",
    "title": "tesla model 3 ",
    "description": "black 3M vinyl getting installed"
  },
  {
    "id": "1ebd6e96-20b9-47be-961b-8aef569ab59f",
    "url": "https://static.wixstatic.com/media/cd12f7_e16d86e3af1d45fcba90bd801e297a09~mv2.jpg",
    "title": "mgb",
    "description": "the start of a fun project client said it cannot be done, well we did it"
  },
  {
    "id": "3f2f486b-2f8b-41a6-8e55-60176ebb9c50",
    "url": "https://static.wixstatic.com/media/cd12f7_7a10739fd4eb4838a6e5ea24a9c15d97~mv2.jpg",
    "title": "tahoe",
    "description": "getting alot of pink trim and wheels installed pink tint and and pink headlight tint"
  },
  {
    "id": "d657f0b7-86de-4347-87fa-3d185b51d613",
    "url": "https://static.wixstatic.com/media/cd12f7_17b91e86f0c1440abfe48898da96dc74~mv2.jpg",
    "title": "mercedes gtr",
    "description": "yellow headlights installed"
  },
  {
    "id": "8bb6a8c0-e72f-47c6-8f58-10c4c8f3d0ea",
    "url": "https://static.wixstatic.com/media/cd12f7_d028c84bf2dc4372bb2934c5387c4d34~mv2.jpg",
    "title": "70932983319__3B7209EE-38B1-4980-98F1-A9BAE5725339.jpg",
    "description": ""
  },
  {
    "id": "4d5042f4-f7be-447c-a3a7-e3367fa45061",
    "url": "https://static.wixstatic.com/media/cd12f7_14d40c933c3940b0ba817a2124026ce9~mv2.jpg",
    "title": "70293764926__77368373-B2B2-40F4-80D7-4E25DBAFACC6.jpg",
    "description": ""
  },
  {
    "id": "91aa19c0-fcee-4cfb-b14c-1ddc0c5a22b5",
    "url": "https://static.wixstatic.com/media/cd12f7_14d40c933c3940b0ba817a2124026ce9~mv2.jpg",
    "title": "70293764926__77368373-B2B2-40F4-80D7-4E25DBAFACC6.jpg",
    "description": ""
  },
  {
    "id": "a414394a-043e-47a6-8e60-7019c3b6ee40",
    "url": "https://static.wixstatic.com/media/cd12f7_099fac538e1d4ae6b20196cb814439ad~mv2.jpg",
    "title": "70162966412__1A12890A-37E3-4DC0-A8D2-8D4BF24164D8.jpg",
    "description": ""
  },
  {
    "id": "64d4c529-0354-4d22-83d8-6cfe3314becb",
    "url": "https://static.wixstatic.com/media/cd12f7_bdeba28f88fe47329c8743120454d153~mv2.jpg",
    "title": "mclaren 720s",
    "description": "30% windshield tint 5% sides and rear tint"
  },
  {
    "id": "110b2529-962a-4786-bf74-fe65c216b565",
    "url": "https://static.wixstatic.com/media/cd12f7_7828778d482f4696bff44fac651d83f3~mv2.jpg",
    "title": "69194751242__F6CE6922-EF33-4240-9022-10F3B041B66B.jpg",
    "description": ""
  },
  {
    "id": "a18f1a1f-eae6-4316-a19a-4cb0fa69aac1",
    "url": "https://static.wixstatic.com/media/cd12f7_4164f0ba39c74845a9af1ff9924aa9bc~mv2.jpg",
    "title": "69194751242__F6CE6922-EF33-4240-9022-10F3B041B66B.jpg",
    "description": ""
  },
  {
    "id": "c22872fd-9fb9-4a3f-9cd1-c870d5348a5c",
    "url": "https://static.wixstatic.com/media/cd12f7_c46f5cdc9fb7426587b4ea34b448003c~mv2.png",
    "title": "67219726043__D86B5B29-B6FF-45DE-8507-B119690C2B28.HEIC",
    "description": ""
  },
  {
    "id": "23e2374e-36f6-48f1-af26-dec28dee612a",
    "url": "https://static.wixstatic.com/media/cd12f7_3f0c5346e62649859923aaa892de5c23~mv2.jpg",
    "title": "chevelle",
    "description": "full tint getting installed 15% this is the start of a long journey with this one"
  },
  {
    "id": "54daa666-61a7-455f-b463-e30cbee0288f",
    "url": "https://static.wixstatic.com/media/cd12f7_4d9b99aac9314d819af27ce6d8763f82~mv2.png",
    "title": "66380877868__A29D9BA6-4A5B-483E-ABC7-1DC2E71CDDFB.HEIC",
    "description": ""
  },
  {
    "id": "c8f44df1-3ac5-467f-bba3-b1f57dd2022b",
    "url": "https://static.wixstatic.com/media/cd12f7_ac004470386b405c971b8c527e1e683a~mv2.png",
    "title": "66380870829__496F4A85-9367-44A4-A978-5F8C604FB7AB.HEIC",
    "description": ""
  },
  {
    "id": "8c11b4c2-7823-431e-8a30-9e15f92c41bd",
    "url": "https://static.wixstatic.com/media/cd12f7_e646caefc83b41d6a35637f2acb795c8~mv2.png",
    "title": "66380870001__00D02244-0912-4ACB-AE53-E1BCE6F04CCF.HEIC",
    "description": ""
  },
  {
    "id": "d9d24228-38d9-44ba-8688-fab8ede21e5f",
    "url": "https://static.wixstatic.com/media/cd12f7_8f0bfee781434310a12f8b4c28cb1463~mv2.png",
    "title": "66378437746__5CF60C04-B4DA-4B49-94BE-3C938033B9EC.HEIC",
    "description": ""
  },
  {
    "id": "9a66a73d-e9f0-4b71-89f8-e4cbb29e0463",
    "url": "https://static.wixstatic.com/media/cd12f7_5ac1d9ca15a8452097fd086244b4764d~mv2.png",
    "title": "66362937561__8315A455-F2AB-4D4D-88D7-BFEDAC159C64.HEIC",
    "description": ""
  },
  {
    "id": "11bdeb14-fbdd-46da-ad05-e3678e7f8219",
    "url": "https://static.wixstatic.com/media/cd12f7_8e5d54ccca3d4ec494878c7d7c0388df~mv2.png",
    "title": "66250730897__8219DCB8-2137-4BD3-9D46-0A2F153481FC.HEIC",
    "description": ""
  },
  {
    "id": "900da094-993e-4ff0-a439-51fcdf799d04",
    "url": "https://static.wixstatic.com/media/cd12f7_183fd4ca4cd64ce187180490cbdc59a6~mv2.png",
    "title": "65880459801__5ED9CB0C-86A7-4E08-8245-880501760BD2.HEIC",
    "description": ""
  },
  {
    "id": "b146361a-9a36-4607-8ebd-78470581f497",
    "url": "https://static.wixstatic.com/media/cd12f7_0f5e07c0287b4b25964427104272a335~mv2.png",
    "title": "porsche 911",
    "description": "full SATIN CLEAR BRA/ PPF (paint protection film)"
  },
  {
    "id": "5ce01fbe-e76f-425a-aee5-6f06935a1ce5",
    "url": "https://static.wixstatic.com/media/cd12f7_0f625ad84bd54cc98089b9b8bc47f638~mv2.jpg",
    "title": "2020 rzr turbo 4 seater",
    "description": "satin clear bra/PPF (PAINT PROTECTION FILM)"
  },
  {
    "id": "551cd9c0-b38c-42cb-9c42-3a72740d16f4",
    "url": "https://static.wixstatic.com/media/cd12f7_98026d2ed8264cf4895071e5a8752b26~mv2.jpg",
    "title": "456D2DA7-D8E4-4998-9AB7-D7788C34E21E.JPG",
    "description": ""
  },
  {
    "id": "66049167-fc24-4414-88b3-07b1230e3549",
    "url": "https://static.wixstatic.com/media/cd12f7_348fbbded5ee47c1b485f4fcc0d38456~mv2.jpg",
    "title": "2018 subaru sti",
    "description": "custom vis carbon fiber hood protected in 3M clear bra"
  },
  {
    "id": "91d6efe5-2663-4cc4-8869-4bd8de3756af",
    "url": "https://static.wixstatic.com/media/cd12f7_9507669ae1a44244b919ba10ceadf245~mv2.jpg",
    "title": "2D6FBF32-0C19-4BD8-BE48-13A1D515A0E8.jpg",
    "description": ""
  },
  {
    "id": "295359e2-8e9a-426e-a94f-177729d4e8d5",
    "url": "https://static.wixstatic.com/media/cd12f7_fa0966ad3ff14cd9ad4d59be57acec38~mv2.jpg",
    "title": "2769AE68-9737-460D-B59B-3E766E1AD350.jpg",
    "description": ""
  },
  {
    "id": "fe87f222-ee75-41ee-b391-d9bf1c247f1a",
    "url": "https://static.wixstatic.com/media/cd12f7_fdc7fe3f240241bea2c0a256279264cf~mv2.jpg",
    "title": "",
    "description": ""
  },
  {
    "id": "d86f65a4-f8b8-464a-9dc2-7ed30315917e",
    "url": "https://static.wixstatic.com/media/cd12f7_fdc7fe3f240241bea2c0a256279264cf~mv2.jpg",
    "title": "",
    "description": ""
  },
  {
    "id": "20178c49-a35b-43c8-b3e2-f8fa5432689f",
    "url": "https://static.wixstatic.com/media/cd12f7_fafe415d467f466984eb041560d6a070~mv2.jpg",
    "title": "chevelle and del sol",
    "description": "full tint on chevelle "
  },
  {
    "id": "aaee8c0f-3f0c-43a9-9de6-1e377a391895",
    "url": "https://static.wixstatic.com/media/cd12f7_abc4805278de4f53a9323a3b723abb54~mv2.jpg",
    "title": "2020 mazda miata RF",
    "description": "full front clear bra/ PPF (paint protection film)"
  },
  {
    "id": "0e1df81e-965f-45a3-89d1-c550f4e533b6",
    "url": "https://static.wixstatic.com/media/cd12f7_29cd0d0cfa14425fa5f2d60765ff8cf9~mv2.jpg",
    "title": "2001 s2k full tint 20% sides and rear 50% windshield ",
    "description": ""
  },
  {
    "id": "d6282287-c787-457f-a2c4-95724087b47d",
    "url": "https://static.wixstatic.com/media/cd12f7_690300fbec3b4bd9ba213a788b4419de~mv2.jpg",
    "title": "Big stretch on the hood on the Supra one piece ",
    "description": ""
  },
  {
    "id": "d913261e-2b38-49d9-8f9e-f3a01c102f65",
    "url": "https://static.wixstatic.com/media/cd12f7_61e5e90089be4e95af48bffc62a0b996~mv2.jpg",
    "title": "2024 gr Supra full body color change PPF/ clear bra in purple stek",
    "description": ""
  },
  {
    "id": "8e9ba623-9958-4b43-9d7b-424d9876d484",
    "url": "https://static.wixstatic.com/media/cd12f7_e2a25af9bf3a4d61b3c9e5028accc6fb~mv2.jpg",
    "title": "2018 jaguar 70% windshield ",
    "description": ""
  },
  {
    "id": "5d55838e-d7c0-4040-b11f-349dae791718",
    "url": "https://static.wixstatic.com/media/cd12f7_3657f75ae3324f91b2c5695dbb41b69b~mv2.jpg",
    "title": "2024 Audi sq5 taillight tint ",
    "description": ""
  },
  {
    "id": "6073eba6-e98e-42bb-b70d-69cdaea020fb",
    "url": "https://static.wixstatic.com/media/cd12f7_c1dbf31217334fef9cf9ecee31c9622f~mv2.jpg",
    "title": "Audi r8 full tint 15% sides ",
    "description": ""
  },
  {
    "id": "26777ebf-d5e6-405d-972e-66814d935d06",
    "url": "https://static.wixstatic.com/media/cd12f7_df906f51e4a144de9395da9c51b8f2d0~mv2.jpg",
    "title": "2024 green ford raptor front end PPF/clear bra ",
    "description": ""
  },
  {
    "id": "2719dbd9-8dff-431b-95b8-3d7b32b5b217",
    "url": "https://static.wixstatic.com/media/cd12f7_f93bba20913f411fb8fcb69193b33593~mv2.jpg",
    "title": "Wrapped the top of this gmc in white for Les Schwab ",
    "description": ""
  },
  {
    "id": "8f4bda65-d0d5-481a-a554-87f068f89235",
    "url": "https://static.wixstatic.com/media/cd12f7_5d4c969b5c694df2b7a99bc9d493c929~mv2.jpg",
    "title": "IMG_0024.jpg",
    "description": ""
  },
  {
    "id": "98e61b89-b4fa-4bf4-8946-559a5300a16e",
    "url": "https://static.wixstatic.com/media/cd12f7_12c8c61511b14fb59520b01e7bbfc342~mv2.jpg",
    "title": "2024 grand Cherokee 5% tint sides and rear 35% windshield ",
    "description": ""
  },
  {
    "id": "fe3318cc-b99e-4ed4-a558-2665dbd5f08e",
    "url": "https://static.wixstatic.com/media/cd12f7_fba11bc5442841318adc14b38d26d910~mv2.jpg",
    "title": "2024 G wagon full body satin PPF/clear bra in stek dynomatt and 35% tint ",
    "description": ""
  },
  {
    "id": "1ba7881e-0f89-4d27-a79e-ad8080e95291",
    "url": "https://static.wixstatic.com/media/cd12f7_d1fba8dfe75248708284a522915e9e7f~mv2.jpg",
    "title": "IMG_0086.jpg",
    "description": ""
  },
  {
    "id": "00c40338-ddd8-4357-b71d-e7b9bbb82f19",
    "url": "https://static.wixstatic.com/media/cd12f7_b888a824f8e04ebf8c4e280efc504e9c~mv2.jpg",
    "title": "IMG_0085.jpg",
    "description": ""
  },
  {
    "id": "88f04af8-4e8e-46b1-a8ef-db3f9d248f1d",
    "url": "https://static.wixstatic.com/media/cd12f7_0fe9a081e0834ec7a05ccec9cf4bed3f~mv2.jpg",
    "title": "IMG_1160.jpg",
    "description": ""
  },
  {
    "id": "d36eed2f-bbf1-4f59-83c4-a94830536ec8",
    "url": "https://static.wixstatic.com/media/cd12f7_26bc9cddddab450985474ec3aad472ea~mv2.jpg",
    "title": "IMG_1158.jpg",
    "description": ""
  },
  {
    "id": "386cc9fa-a193-46db-b677-56147de4513c",
    "url": "https://static.wixstatic.com/media/cd12f7_96a5e6ae053d4ef8a20d11adcca02b7d~mv2.jpg",
    "title": "IMG_1129.jpg",
    "description": ""
  },
  {
    "id": "ee7e8ca0-a5a9-4722-8efe-9b29dd603390",
    "url": "https://static.wixstatic.com/media/cd12f7_92aa0d315bad40c2b692cc2bc7908650~mv2.jpg",
    "title": "IMG_1132.jpg",
    "description": ""
  },
  {
    "id": "1fc947e1-d52a-4321-a166-30f27301aad7",
    "url": "https://static.wixstatic.com/media/cd12f7_5d823aa47cf848e3a33c909b1efa8211~mv2.jpg",
    "title": "IMG_1131.jpg",
    "description": ""
  },
  {
    "id": "38d0b73b-f185-4731-b499-4e26ef91a1e7",
    "url": "https://static.wixstatic.com/media/cd12f7_023860ccabfb4cd593bd38e2fd2b4076~mv2.jpg",
    "title": "IMG_1130.jpg",
    "description": ""
  },
  {
    "id": "3c06ec2e-ab66-4af5-b637-dd42ccb7885c",
    "url": "https://static.wixstatic.com/media/cd12f7_ff7d31ba1d4946db8d20d7d5fd2fbb1b~mv2.jpg",
    "title": "IMG_1122.jpg",
    "description": ""
  },
  {
    "id": "17c3da49-7119-45ff-84b7-f07d99de8607",
    "url": "https://static.wixstatic.com/media/cd12f7_0a83038e150d45c3b6eab72032f2b261~mv2.jpg",
    "title": "IMG_1114.jpg",
    "description": ""
  },
  {
    "id": "7cadba91-f251-4386-8b78-5a20029b1248",
    "url": "https://static.wixstatic.com/media/cd12f7_4287282479be42baa2a16074262d92b9~mv2.jpg",
    "title": "IMG_1111.jpg",
    "description": ""
  },
  {
    "id": "72e831dd-518e-4fb5-9eb7-b67a1ad40ec9",
    "url": "https://static.wixstatic.com/media/cd12f7_332caa5bb9e5409d980f37d6fad331c3~mv2.jpg",
    "title": "IMG_1103.jpg",
    "description": ""
  },
  {
    "id": "3e3db08c-73a8-4819-8a76-43d9907aa634",
    "url": "https://static.wixstatic.com/media/cd12f7_5bc7e74e856f499384f2b6f5a4a28484~mv2.jpg",
    "title": "IMG_1082.jpg",
    "description": ""
  },
  {
    "id": "d481f16b-a7de-4dcb-ad23-2cf89bdd38a7",
    "url": "https://static.wixstatic.com/media/cd12f7_ee975ee9b3a9472abebc40aab14a6aa0~mv2.jpg",
    "title": "IMG_0568.jpg",
    "description": ""
  },
  {
    "id": "7e0a2ea2-ea9b-45b1-8c75-e542b06002e5",
    "url": "https://static.wixstatic.com/media/cd12f7_decefc888ebc4691b5c8d21de10bb0a7~mv2.jpg",
    "title": "IMG_0566.jpg",
    "description": ""
  },
  {
    "id": "54412902-2479-4aa3-ab8b-babeab68900a",
    "url": "https://static.wixstatic.com/media/cd12f7_b2cf8d176535429ca9a9abe4e7957684~mv2.jpg",
    "title": "IMG_0554.jpg",
    "description": ""
  },
  {
    "id": "4c16ed39-485e-40f7-90aa-bb7b7154e3aa",
    "url": "https://static.wixstatic.com/media/cd12f7_3fadfa236f6d4ced96c2c28525d05201~mv2.jpg",
    "title": "IMG_0537.jpg",
    "description": ""
  },
  {
    "id": "b74d088e-b1aa-4b91-8ab4-1b20d6b4090c",
    "url": "https://static.wixstatic.com/media/cd12f7_484a05c178044fba8307d534c85b16a1~mv2.jpg",
    "title": "IMG_0528.jpg",
    "description": ""
  },
  {
    "id": "a0019300-ec5b-413e-ba3e-c455047c7cfe",
    "url": "https://static.wixstatic.com/media/cd12f7_8730ef4715f04997abfa7c054da5e47d~mv2.jpg",
    "title": "IMG_0522.jpg",
    "description": ""
  },
  {
    "id": "331715da-874a-4518-9114-8e6cdbf79846",
    "url": "https://static.wixstatic.com/media/cd12f7_97fb9d74a192416a99173363790aad01~mv2.jpg",
    "title": "IMG_0485.jpg",
    "description": ""
  },
  {
    "id": "e0a86dd8-5aff-4159-b01f-ff085f99787e",
    "url": "https://static.wixstatic.com/media/cd12f7_58fd6971f7a84ae798fb69f20f56d732~mv2.jpg",
    "title": "IMG_0486.jpg",
    "description": ""
  },
  {
    "id": "a52e9579-1f37-42d9-b158-d1fd1003d086",
    "url": "https://static.wixstatic.com/media/cd12f7_b36635803faf4548a1cc391509d11e6e~mv2.jpg",
    "title": "IMG_0483.jpg",
    "description": ""
  },
  {
    "id": "22458e75-e264-41f1-a001-5303e61ebb4c",
    "url": "https://static.wixstatic.com/media/cd12f7_bc9ca61198284e4bba0be4d2e3014faf~mv2.jpg",
    "title": "IMG_0469.jpg",
    "description": ""
  },
  {
    "id": "df65c360-03cc-459b-b717-b9cf50514424",
    "url": "https://static.wixstatic.com/media/cd12f7_f43db9228a184fc5a26eb2127b2042e3~mv2.jpg",
    "title": "IMG_0437.jpg",
    "description": ""
  },
  {
    "id": "9df239d7-c38d-4f50-8a4c-a4cd493b09d7",
    "url": "https://static.wixstatic.com/media/cd12f7_7cfec649162a43e1999c91a6f53325f5~mv2.jpg",
    "title": "IMG_0439.jpg",
    "description": ""
  },
  {
    "id": "4ac3c178-a09a-4320-b647-e0f3d542f410",
    "url": "https://static.wixstatic.com/media/cd12f7_813fecddadfd44409b5a1f25458a2105~mv2.jpg",
    "title": "1A0FB7D3-EA75-47AF-BEB2-C3D75E33ADF1.jpg",
    "description": ""
  },
  {
    "id": "6f02aee6-735d-4baa-985a-02fabda355e1",
    "url": "https://static.wixstatic.com/media/cd12f7_fe8f4cad66764c608a6a44bba489192f~mv2.jpg",
    "title": "IMG_0430.jpg",
    "description": ""
  },
  {
    "id": "cd8d6dd6-b41e-44a6-969b-9929b02cfe33",
    "url": "https://static.wixstatic.com/media/cd12f7_56838f935af043df8fc8c329651e2474~mv2.jpg",
    "title": "IMG_0427.jpg",
    "description": ""
  },
  {
    "id": "b9786fc6-d690-4e90-9ca0-86d967825605",
    "url": "https://static.wixstatic.com/media/cd12f7_e1fa8904a8244b96b5f1ed2fdbe2f33a~mv2.jpg",
    "title": "IMG_0411.jpg",
    "description": ""
  },
  {
    "id": "505d77c6-b866-446e-a122-62aad460fe7d",
    "url": "https://static.wixstatic.com/media/cd12f7_3f79fc49f2d74c2c879a8fdde0aa29b4~mv2.jpg",
    "title": "IMG_0408.jpg",
    "description": ""
  },
  {
    "id": "83a01d40-bb6a-48dc-b002-d99e5b398b87",
    "url": "https://static.wixstatic.com/media/cd12f7_544a3a02f2664a11bd050cfa055839a3~mv2.jpg",
    "title": "IMG_0406.jpg",
    "description": ""
  },
  {
    "id": "a61f1d2a-edb2-41f0-89f5-4e89c7f91a90",
    "url": "https://static.wixstatic.com/media/cd12f7_2f7ca9c019c14efc86e242112fe82aa0~mv2.jpg",
    "title": "IMG_0402.jpg",
    "description": ""
  },
  {
    "id": "647f1524-80a6-420a-aaf8-f344b6e3371a",
    "url": "https://static.wixstatic.com/media/cd12f7_926caa8f195b4e7fa37669927c7dba02~mv2.jpg",
    "title": "IMG_0399.jpg",
    "description": ""
  }
];

// **Generate Cloudinary API Signature**
function generateSignature(params) {
  const filteredParams = Object.keys(params)
    .filter(key => params[key] !== undefined && params[key] !== '') // Remove undefined or empty values
    .sort()
    .map(key => `${key}=${params[key]}`)
    .join('&');

  return crypto.createHash('sha1').update(filteredParams + API_SECRET).digest('hex');
}

// **Upload function for a single image**
async function uploadImage(image) {
  try {
    const timestamp = Math.floor(Date.now() / 1000);

    // Signed parameters
    const params = {
      upload_preset: UPLOAD_PRESET,
      folder: FOLDER_NAME,
      timestamp,
      public_id: image.id, // Unique identifier
      context: `alt=${image.description || ""}|caption=${image.title}`
    };

    // Generate Cloudinary signature
    const signature = generateSignature(params);

    const formData = new FormData();
    formData.append('file', image.url); // Upload using existing URL (Cloudinary's recommended approach)
    formData.append('upload_preset', UPLOAD_PRESET);
    formData.append('api_key', API_KEY);
    formData.append('timestamp', timestamp);
    formData.append('signature', signature);
    formData.append('folder', FOLDER_NAME);
    formData.append('context', params.context);
    formData.append('public_id', image.id); // Ensures unique filename

    const response = await axios.post(
      `https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`,
      formData,
      { headers: formData.getHeaders() }
    );

    console.log(`✅ Uploaded: ${image.title} - ${response.data.secure_url}`);

    return {
      id: image.id,
      url: response.data.secure_url,
      title: image.title,
      description: image.description
    };
  } catch (error) {
    console.error(`❌ Error uploading ${image.title}:`, error.response?.data || error.message);
    return null;
  }
}

// **Upload function in batches of 10 (following Cloudinary best practices)**
async function uploadInBatches(batchSize = 10) {
  let uploadedImages = [];

  for (let i = 0; i < images.length; i += batchSize) {
    const batch = images.slice(i, i + batchSize);
    console.log(`🚀 Uploading batch ${i / batchSize + 1}/${Math.ceil(images.length / batchSize)}...`);

    const results = await Promise.all(batch.map(uploadImage));
    uploadedImages.push(...results.filter(img => img !== null));

    console.log(`✅ Batch ${i / batchSize + 1} completed.`);
    await new Promise(resolve => setTimeout(resolve, 2000)); // Delay to prevent API rate limits
  }

  console.log(`🎉 All images uploaded! Total: ${uploadedImages.length}`);

  // **Save uploaded images to a JavaScript file**
  const jsContent = `export const images = ${JSON.stringify(uploadedImages, null, 2)};`;
  fs.writeFileSync('uploadedImages.js', jsContent);

  console.log('✅ Saved uploaded images to uploadedImages.js');
}

// **Start bulk upload**
uploadInBatches(10);
