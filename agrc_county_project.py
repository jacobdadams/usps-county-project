import arcpy
import os
import csv
from time import strftime

uniqueRunNum = strftime("%Y%m%d_%H%M%S")


countyFipsDomain = {
    49025: 'KANE',
    49027: 'MILLARD',
    49039: 'SANPETE',
    49007: 'CARBON',
    49049: 'UTAH',
    49005: 'CACHE',
    49043: 'SUMMIT',
    49053: 'WASHINGTON',
    49019: 'GRAND',
    49047: 'UINTAH',
    49045: 'TOOELE',
    49041: 'SEVIER',
    49017: 'GARFIELD',
    49003: 'BOX ELDER',
    49021: 'IRON',
    49057: 'WEBER',
    49015: 'EMERY',
    49033: 'RICH',
    49051: 'WASATCH',
    49001: 'BEAVER',
    49009: 'DAGGETT',
    49011: 'DAVIS',
    49055: 'WAYNE',
    49031: 'PIUTE',
    49029: 'MORGAN',
    49035: 'SALT LAKE',
    49013: 'DUCHESNE',
    49023: 'JUAB',
    49037: 'SAN JUAN'
}
fixedTxtFields = [
    'CCONTACT NAME',
    'COMPANY NAME',
    'ADDRESS LINE',
    'CITY',
    'STATE',
    'ZIP5',
    'ZIP4',
    'CONGRESSIONAL CODE',
    'COUNTY CODE',
    'FILLER',
    'Key',
    'LATITUDE',
    'LONGITUDE',
]
fixedTxtFieldLengths = [
    42,
    66,
    66,
    28,
    2,
    5,
    4,
    4,
    5,
    19,
    50,
    15,
    15,
]


def createFixedLengthText(row):
        fieldLengths = fixedTxtFieldLengths
        try:
            fields = list(row)
            for i in range(11):
                fields[i] = fields[i][:fieldLengths[i]] + (fieldLengths[i] - len(fields[i])) * ' '
                if len(fields[i]) != fieldLengths[i]:
                    print 'Field length error: {}'.format(fields[i])
            for i in (11, 12):
                fields[i] = (fieldLengths[i] - len(fields[i])) * ' ' + fields[i][:fieldLengths[i]]
                if len(fields[i]) != fieldLengths[i]:
                    print 'Field length error: {}'.format(fields[i])
        except:
            print row

        return ''.join(fields)


def createCsvRow(row):
    try:
        fields = list(row)
        fields[2] = fields[2].upper()
        fields[3] = fields[3].upper()
        fields[6] = ''
        fields[-1] = fields[-1][:15]
        fields[-2] = fields[-2][:15]
    except:
        print row

    return ','.join(fields)


if __name__ == '__main__':
    print uniqueRunNum
    county_ids = ['49009']
    output_folder = r'C:\GisWork\UspsCountyProject\DAGGETT'
    addressPointsWorkspace = 'C:\Users\kwalker\Documents\ArcGIS\Projects\Daggett Structure Address Points\Daggett Structure Address Points.gdb'
    addressPoints = 'DaggetAddrPntsWithStructure'
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    sgid_connection = r'Database Connections\Connection to sgid.agrc.utah.gov.sde'
    outputGdb_name = 'outputs.gdb'
    countyProjectTemplate = r'County_Project_Submission_Template.gdb\CP_Submit_template'

    addressPoints = os.path.join(addressPointsWorkspace, addressPoints)

    congressionalDistricts = os.path.join(sgid_connection, 'SGID10.POLITICAL.USCongressDistricts2012')
    addrPointsWithDistrict = os.path.join(output_folder, outputGdb_name, 'addressPointsProject' + uniqueRunNum)
    outputGdb = os.path.join(output_folder, outputGdb_name)
    if not arcpy.Exists(outputGdb):
        arcpy.CreateFileGDB_management(output_folder, outputGdb_name)

    # Fields to be converted to USPS county project format.
    # 'CountyID', 'FullAdd', 'City', 'ZipCode' must exist in the addressPoints table.
    addrFields = ['OID@', 'CountyID', 'FullAdd', 'City', 'ZipCode', 'DISTRICT', 'SHAPE@Y', 'SHAPE@X']

    def getFieldI(fieldName):
        return addrFields.index(fieldName)

    countyProject = os.path.join(outputGdb, 'countyProject_{}'.format(uniqueRunNum))
    arcpy.CreateFeatureclass_management(outputGdb,
                                        'countyProject_{}'.format(uniqueRunNum),
                                        template=countyProjectTemplate)
    countyProjectFields = ['NAME', 'COMPANYNAME', 'ADDRESSLINE',
                           'CITY', 'STATE', 'ZIP5',
                           'ZIP4', 'CONGRESSIONALCODE', 'COUNTYCODE',
                           'FILLER', 'KEY', 'LATITUDE',
                           'LONGITUDE']
    counties = {
        'KANE': [],
        'MILLARD': [],
        'SANPETE': [],
        'CARBON': [],
        'UTAH': [],
        'CACHE': [],
        'SUMMIT': [],
        'WASHINGTON': [],
        'GRAND': [],
        'UINTAH': [],
        'TOOELE': [],
        'SEVIER': [],
        'GARFIELD': [],
        'BOX ELDER': [],
        'IRON': [],
        'WEBER': [],
        'EMERY': [],
        'RICH': [],
        'WASATCH': [],
        'BEAVER': [],
        'DAGGETT': [],
        'DAVIS': [],
        'WAYNE': [],
        'PIUTE': [],
        'MORGAN': [],
        'SALT LAKE': [],
        'DUCHESNE': [],
        'JUAB': [],
        'SAN JUAN': []
    }
    # Set with county_ids list
    county_selection_where = None
    if len(county_ids) > 0:
        county_selection_where = "CountyID IN ('{}')".format("'','".join([str(c) for c in county_ids]))
    address_layer = 'addrpoints_' + uniqueRunNum
    arcpy.MakeFeatureLayer_management(addressPoints, address_layer, county_selection_where)

    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4326)
    arcpy.env.geographicTransformations = 'NAD_1983_To_WGS_1984_5'
    arcpy.Identity_analysis(address_layer, congressionalDistricts, addrPointsWithDistrict)
    # # Set with county_ids list
    # county_selection_where = None
    # if len(county_ids) > 0:
    #     county_selection_where = "CountyID IN ('{}')".format("'','".join([str(c) for c in county_ids]))

    with arcpy.da.SearchCursor(addrPointsWithDistrict, addrFields) as addrPointCursor, \
         arcpy.da.InsertCursor(countyProject, countyProjectFields) as countyProjectCursor:
            # outputCsv = csv.writer(outputFile)
            # outputCsv.writerow(countyProjectFields)
            for addrRow in addrPointCursor:
                countyRow = []
                # County Project NAME
                countyRow.append(countyFipsDomain[int(addrRow[getFieldI('CountyID')])])
                # County Project COMPANYNAME
                countyRow.append('AGRC')
                # County Project ADDRESSLINE
                countyRow.append(addrRow[getFieldI('FullAdd')])
                # County Project CITY
                countyRow.append(addrRow[getFieldI('City')])
                # County Project STATE
                countyRow.append('UT')
                # County Project ZIP5
                countyRow.append(addrRow[getFieldI('ZipCode')])
                # County Project ZIP4
                countyRow.append(0)
                # County Project CONGRESSIONALCODE
                countyRow.append('UT0' + str(addrRow[getFieldI('DISTRICT')]))
                # County Project COUNTYCODE
                countyRow.append('UT' + addrRow[getFieldI('CountyID')][-3:])
                # County Project FILLER
                countyRow.append('')
                # County Project KEY
                countyRow.append(addrRow[getFieldI('OID@')])
                # County Project LATITUDE
                countyRow.append(addrRow[getFieldI('SHAPE@Y')])
                # County Project LONGITUDE
                countyRow.append(addrRow[getFieldI('SHAPE@X')])
                # CountyProject row insert
                countyProjectCursor.insertRow(countyRow)
                # County project rows
                counties[countyRow[0]].append(countyRow)

    headerString = ','.join(countyProjectFields)
    # List will be created for each id in county_ids
    # Output file should be a csv
    for county in counties:
        countyProjectCsv = os.path.join(output_folder, '{}_{}.csv'.format(county, uniqueRunNum))
        row_list = counties[county]
        if len(row_list) > 0:
            with open(countyProjectCsv, 'w') as outputFile:
                outputFile.write(headerString + '\n')
                for row in row_list:
                    try:
                        rowString = createCsvRow([str(x) for x in row])
                        outputFile.write(rowString + '\n')
                    except:
                        print row

                outputFile.write('\n')

    print '! - complete - !'
