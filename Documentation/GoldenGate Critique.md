# Regarding GoldenGate
GoldenGate does offer some useful functions, but its main focus seems to be on dealing with scanned documents. These features are completely useless to us since the publications are encoded as text rather than as images. Ignoring functions catered to scanned documents and thinking only of extracting TNU fields, GoldenGate has the following useful features:

Tagging scientific names
Parsing those names (although not as well as GNParser seems to)

GoldenGate had some other promising plugins like tagging treatment sections, but I’ve tried them personally on multiple publications and they require manual input and don’t produce very useful results. GoldenGate also has very long loading times (minutes for a single publication).

The two usable functions offered by GoldenGate (which is written in oracle java) are available by combining GNParser and GNRD. GNParser can be used as a webservice (runtimes are very short, could deal with hundreds of names in a fraction of a second), and GNRD is written in ruby and also has a web service available as well. The GoldenGate repository has not been updated in ~4 years while GlobalNames is being regularly maintained. 

I did not intentionally pick two GlobalNames projects. I found GNParser a few weeks into the project and GNRD is one of the most recent and well established scientific name extraction tools published. For comparison TaxonGrab (which is used by GoldenGate to extract scientific names) was published in 2005 while GRND was put out around 2016. There were four other programs published in between the TaxonGrab and GRND each claiming to produce significantly better results compared to their predecessor, so I feel very confident saying GRND is a more suitable tool than GoldenGate’s TaxonGrab. 

I don’t think GoldenGate is a useless program, there don’t seem to be any other programs out there that markup publications as thoroughly as it does, but GoldenGate is made up of many small modules and those individual modules are very dated. If we only need a few of GoldenGate’s modules like in this project, it makes much more sense to use something modern.
