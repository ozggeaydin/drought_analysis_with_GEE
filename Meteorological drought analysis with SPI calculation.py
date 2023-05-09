var worldcountries = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017');
var filterCountry = ee.Filter.eq('country_na', 'Turkey');
var country = worldcountries.filter(filterCountry);  


var chirps_filtered_year = ee.ImageCollection.fromImages(ee.List.sequence(1981, 2020).map(function(year){
  var chirps_sum = imageCollection.filter(ee.Filter.calendarRange(year,year,'year'))
  .filter(ee.Filter.calendarRange(3,7,'month'))
  .reduce(ee.Reducer.sum())
  .set('system:time_start', ee.Date.fromYMD(year,7,1).millis())
  .rename("sum")
  .clip(country);
  return chirps_sum;
}));

print("40 tane 3 aylık toplam yağış", chirps_filtered_year)

var chirps_mean =  chirps_filtered_year
                        .reduce(ee.Reducer.mean())
                        .rename("mean_longterm");
                        
print("toplam ortalama", chirps_mean)

var chirps_std = chirps_filtered_year
                        .reduce(ee.Reducer.stdDev())
                        .rename("std");
                        
print("chiprs_std" ,chirps_std)            

var SPI = chirps_filtered_year.map(function(image){
  var time = image.get('system:time_start')
  return image.expression("(image-mean)/std",
  {
    "image": image.select("sum"),
    "mean": chirps_mean.select("mean_longterm"),
    "std": chirps_std.select("std")
  }).rename("SPI").set('system:time_start',time);
});

print("SPI",SPI)

Map.centerObject(country);

var min = ee.Number(SPI.min().reduceRegion({
   reducer: ee.Reducer.min(),
   geometry: country,
   scale: 1000,
   maxPixels: 1e9
   }).values().get(0));
print(min, 'min');

var max = ee.Number(SPI.max().reduceRegion({
   reducer: ee.Reducer.max(),
   geometry: country,
   scale: 1000,
   maxPixels: 1e9
   }).values().get(0));
print(max, 'max');

Map.centerObject(country);

/*
var chart =
    ui.Chart.image
        .series({
          imageCollection: SPI,
          region: country,
          reducer: ee.Reducer.mean(),
          scale: 1000,
          xProperty: 'system:time_start'
        })
        .setSeriesNames(['SPI'])
        .setOptions({
          title: '2000-2020 Yılları CHIRPS Verileri ile Türkiye Yağış Durumu',
          hAxis: {title: 'Tarih', titleTextStyle: {italic: false, bold: true}},
          vAxis: {
            title: 'Aylar',
            titleTextStyle: {italic: false, bold: true}
          },
          lineWidth: 5,
          colors: ['e37d05', '1d6b99',"0aab1e","ff4a2d"],
          curveType: 'function'
        });
print(chart);
*/

var SPIVis = {
  min: -3.2,
  max: 4.2,
  palette: ["000000" ,"000000","000000","000000","000000" ,
  "000000","000000","000000","000000" ,"000000",
  "000000","000000",
  "663200","663200","663200","663200","CC3200","CC3200","CC3200","FE9966","FE9966","FE9966","FE9966","FE9966",
  "FEFE00","FEFE00","FEFE00","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff",
  "98FE00","98FE00","98FE00","15CC66","15CC66","15CC66","15CC66","15CC66","339966" ,"339966" ,"339966" ,"0000FF","0000FF",
  "0000FF","0000FF",
  "9900FF","9900FF" ,"9900FF","9900FF","9900FF","9900FF","9900FF","9900FF","9900FF","9900FF" ,
  "9900FF","9900FF","9900FF","9900FF","9900FF","9900FF","9900FF","9900FF","9900FF","9900FF",
  "9900FF","9900FF"]
};
var filteredSPI = SPI.filterDate("2000-01-01","2020-12-31");
var count = filteredSPI.size();
var imageSetCollection = filteredSPI.toList(count)

print(imageSetCollection)

ee.List.sequence(0,ee.Number(count.subtract(1))).getInfo()
.map(function(img){
  // print(img)
  var image = ee.Image(imageSetCollection.get(img))
  Map.addLayer(image, SPIVis)
  
})

Map.centerObject(country);



/*
var outline = ee.Image().byte().paint({
  featureCollection: country,
  color: 1,
  width: 3
});

var toexport = filteredSPI.map(function(image){
         return  ee.Image.constant(0).visualize({palette: ['ffffff']}).clip(geometry)
              .blend(image.select("SPI").visualize(SPIVis))
              .blend(outline)
})

var count = toexport.size();
var imageSetCollection = toexport.toList(count);

ee.List.sequence(0,ee.Number(count.subtract(1))).getInfo()
.map(function(img){
        var image = ee.Image(imageSetCollection.get(img));
        var thumbnail3 = image.getThumbURL({
        'dimensions': 2000,
        'crs': 'EPSG:3857'});
  print('Linear ring region and specified crs', thumbnail3);
});

Map.centerObject(country);
*/
