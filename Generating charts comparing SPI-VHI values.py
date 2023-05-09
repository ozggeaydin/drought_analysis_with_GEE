 

var chirps_filtered_year = ee.ImageCollection.fromImages(ee.List.sequence(1981, 2020).map(function(year){
  var chirps_sum = imageCollection.filter(ee.Filter.calendarRange(year,year,'year'))
  .filter(ee.Filter.calendarRange(6,8,'month'))
  .reduce(ee.Reducer.sum())
  .set('system:time_start', ee.Date.fromYMD(year,7,1).millis())
  .rename("sum")
  .clip(country)
;
  return chirps_sum;
}));

print("21 tane 3 aylık toplam yağış", chirps_filtered_year)

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

var filteredSPI = SPI.filterDate("2000-01-01","2020-12-31")

print("filteredSPI",filteredSPI)
var SPIVis = {
  min: -2.7,
  max: 4.2,
  palette: ["000000" ,"000000" ,"000000" ,"000000" ,"000000" ,"000000" ,"000000" ,"663200","663200","663200",
  "663200","CC3200","CC3200","CC3200","FE9966","FE9966","FE9966","FE9966","FE9966","FEFE00","FEFE00","FEFE00",
  "ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","ffffff","98FE00","98FE00","98FE00",
  "15CC66","15CC66","15CC66","15CC66","15CC66","339966" ,"339966" ,"339966" ,"0000FF","0000FF","0000FF","0000FF","9900FF",
  "9900FF" ,"9900FF" ,"9900FF" ,"9900FF" ,"9900FF" ,"9900FF" ,"9900FF" ,"9900FF" ,"9900FF" ,"9900FF" ,"9900FF" ,"9900FF",
  "9900FF" ,"9900FF" ,"9900FF" ,"9900FF" ,"9900FF" ,"9900FF" ,"9900FF" ,"9900FF" ,"9900FF"],
};

Map.centerObject(country);


////////////////////////////////////////////


////// 20 YILIN SADECE TEMMUZ AYLARI İÇİN VHI HESABI

var start_time = ee.Date('2000-01-01');
var end_time   = ee.Date('2020-12-31');

// Load a dataset
var modis = ee.ImageCollection("MODIS/006/MOD09A1")
              .filterBounds(country);
             
var LST_Data = ee.ImageCollection("MODIS/006/MOD11A2")
                  .filterBounds(country)
                  .select('LST_Day_1km');

  // convert LST to celcius
var toCelsius = function(image){
  var time = image.get('system:time_start')
  var celsius = image.multiply(0.02) // scale factor
                     .subtract(273.15) // from kelvin to C
                     .rename("Celcius")
                     .set('system:time_start',time)
  return celsius;
};

var LST_modis = (LST_Data.map(toCelsius)).select("Celcius")
print("lstmodis", LST_modis)


// NDVI
var addNDVI = function(image) {
   var ndvi = image.normalizedDifference(['sur_refl_b02','sur_refl_b01']);
   var ndvi_th = ndvi.gte(0.1);
   ndvi =  ndvi.updateMask(ndvi_th).rename('ndvi');
   return image.addBands(ndvi);
};    

// Applying NDVI to MODIS dataset
var NDVImodis = modis.map(addNDVI)
                     .select('ndvi')
                     .filterBounds(country)
                     ;
                     
var ndvi_filtered_year = ee.ImageCollection.fromImages(ee.List.sequence(2000, 2020).map(function(year){
  var ndvi_year = NDVImodis.filter(ee.Filter.calendarRange(year,year,'year'))
  .filter(ee.Filter.calendarRange(7,7,'month'))
  .reduce(ee.Reducer.mean())
  .set('system:time_start', ee.Date.fromYMD(year,7,1).millis());
  return ndvi_year;
}));

print("ndvi filtered year", ndvi_filtered_year)

// VCI
var VCI = ndvi_filtered_year.map(function(image){
    return image.expression('(ndvi-min)/(max-min)',
    {
      'ndvi': image.select("ndvi_mean"),
      'min': ndvi_filtered_year.reduce(ee.Reducer.min()),
      'max': ndvi_filtered_year.reduce(ee.Reducer.max())
    })
    .clip(country)
    .rename('VCI')
    .copyProperties(image,['system:time_start']);
});
print("VCI", VCI)

// TCI Calculation
var LST_filtered_year = ee.ImageCollection.fromImages(ee.List.sequence(2000, 2020).map(function(year){
  var LST_year = LST_modis.filter(ee.Filter.calendarRange(year,year,'year'))
  .filter(ee.Filter.calendarRange(7,7,'month'))
  .reduce(ee.Reducer.mean())
  .set('system:time_start', ee.Date.fromYMD(year,7,1).millis());
  return LST_year;
}));
print("LST", LST_filtered_year);

// TCI
var TCI = LST_filtered_year.map(function(image){
    return image.expression('(max-LST)/(max-min)',
    {
      'LST': image.select("Celcius_mean"),
      'min': LST_filtered_year.reduce(ee.Reducer.min()),
      'max': LST_filtered_year.reduce(ee.Reducer.max())
    })
    .clip(country)
    .rename('TCI')
    .copyProperties(image,['system:time_start']);
});
print("TCI", TCI);

//VHI 
var filter = ee.Filter.equals({
  leftField: 'system:time_start',
  rightField: 'system:time_start'
});

var join = ee.Join.saveFirst({
  matchKey: 'match',
});

var both = ee.ImageCollection(join.apply(VCI,TCI,filter))
  .map(function(image) {
    return image.addBands(image.get('match'));
  });
                  
var VHI = both.map(function(img) {
  return img.addBands (
    img.expression('(VCI/2 + TCI/2)*100', {
     'VCI': img.select("VCI"), 
     'TCI': img.select("TCI"),
    }).rename("VHI")).select("VHI");
});
print("VHI", VHI);

// Define Parameters
var VHIVis = {
  min: 0,
  max: 100,
  palette: ["dc2f02","fbb02d","f3de2c","a7c957","73a942","538d22","245501","245501","245501","245501"],
};

var VHI_SPI = ee.ImageCollection(join.apply(VHI,filteredSPI,filter))
  .map(function(image) {
    return image.addBands(image.get('match'));
  });
  
print("VHI_SPI", VHI_SPI)

// Define the chart and print it to the console.

var chart = ui.Chart.image.series({
                                   imageCollection: VHI_SPI ,
                                   region: country ,
                                   scale: 500   ,
                                   xProperty: 'system:time_start'
                                  })
                          .setSeriesNames(['SPI', 'VHI'])
                          .setOptions({
                            title: '2000-2020 Meriç-Ergene Havzası SPI-VHI Grafiği' ,
                            series: {
                                     0: {
                                         targetAxisIndex: 0 ,
                                         type: "line" ,
                                         lineWidth: 5 ,
                                         pointSize: 0 ,
                                         color: "blue" 
                                        } ,
                                     1: {
                                         targetAxisIndex: 1 ,
                                         type: "line" ,
                                         lineWidth: 5 ,
                                         pointSize: 0 ,
                                         color: "green" 
                                        } ,
                                    } ,
                            hAxis: {
                                    title: 'Tarih' ,
                                    titleTextStyle: { italic: false, bold: true }
                                   } ,
                            vAxis: {
                                    0: {
                                        title: "GPP (g*C / m^2)" ,
                                        baseline: 0 ,
                                        titleTextStyle: { bold: true , color: 'green' }
                                      } ,
                                    1: {
                                        title: "LAI" ,
                                        baseline: 0  ,
                                        titleTextStyle: { bold: true, color: 'blue' }
                                      }
                                   } ,
                            curveType: 'function'
                          });

print(chart);

           