Below is a **concise API reference** for using the OMI-Filetype library through pythonnet.
Only **public members accessible from Python** are documented.

Namespaces:

```
OMI
OMI.Formats.Pck
OMI.Workers.Pck
```

---

# ByteOrder (enum)

Namespace: `OMI`

Specifies byte ordering for binary I/O.

| Value                    | Description              |
| ------------------------ | ------------------------ |
| `ByteOrder.BigEndian`    | Big-endian byte order    |
| `ByteOrder.LittleEndian` | Little-endian byte order |

---

# PckAssetType (enum)

Namespace: `OMI.Formats.Pck`

Identifies the type of asset stored in a `.pck` file.

| Name                  | Value | Description           |
| --------------------- | ----- | --------------------- |
| `SkinFile`            | 0     | `.png` skin           |
| `CapeFile`            | 1     | `.png` cape           |
| `TextureFile`         | 2     | `.png` texture        |
| `UIDataFile`          | 3     | unused                |
| `InfoFile`            | 4     | metadata file         |
| `TexturePackInfoFile` | 5     | texture pack info     |
| `LocalisationFile`    | 6     | localisation file     |
| `GameRulesFile`       | 7     | game rules            |
| `AudioFile`           | 8     | audio archive         |
| `ColourTableFile`     | 9     | colour tables         |
| `GameRulesHeader`     | 10    | game rules header     |
| `SkinDataFile`        | 11    | skins archive         |
| `ModelsFile`          | 12    | model data            |
| `BehavioursFile`      | 13    | behaviour definitions |
| `MaterialFile`        | 14    | entity materials      |

---

# PckFile

Namespace: `OMI.Formats.Pck`

Represents a `.pck` archive.

## Constructors

```
PckFile()
PckFile(int type)
PckFile(int type, int xmlVersion)
```

## Fields

| Name                 | Type     | Description             |
| -------------------- | -------- | ----------------------- |
| `Type`               | `int`    | Archive format type     |
| `xmlVersion`         | `int`    | XML version metadata    |
| `XML_VERSION_STRING` | `string` | Constant `"XMLVERSION"` |

## Properties

| Property     | Type  | Description                     |
| ------------ | ----- | ------------------------------- |
| `AssetCount` | `int` | Number of assets in the archive |

## Methods

### GetPropertyList

```
List<string> GetPropertyList()
```

Returns all unique property keys used across assets.

---

### CreateNewAsset

```
PckAsset CreateNewAsset(string assetName, PckAssetType assetType)
```

Creates and adds a new asset.

---

### CreateNewAsset

```
PckAsset CreateNewAsset(string assetName,
                        PckAssetType assetType,
                        Func<byte[]> dataInitializer)
```

Creates an asset and initializes its data.

---

### HasAsset

```
bool HasAsset(string assetName, PckAssetType assetType)
```

Returns `true` if an asset exists.

---

### GetAsset

```
PckAsset GetAsset(string assetName, PckAssetType assetType)
```

Returns the matching asset.
Throws `KeyNotFoundException` if not found.

---

### TryGetAsset

```
bool TryGetAsset(string assetName,
                 PckAssetType assetType,
                 out PckAsset asset)
```

Python usage:

```
found, asset = pck.TryGetAsset(name, type)
```

---

### GetOrCreate

```
PckAsset GetOrCreate(string assetName, PckAssetType assetType)
```

Returns existing asset or creates one.

---

### Contains

```
bool Contains(string assetName, PckAssetType assetType)
bool Contains(PckAssetType assetType)
```

Checks asset existence.

---

### GetAssetsByType

```
IEnumerable<PckAsset> GetAssetsByType(PckAssetType assetType)
```

Returns all assets of the given type.

---

### AddAsset

```
void AddAsset(PckAsset asset)
```

Adds an asset to the archive.

---

### GetAssets

```
IReadOnlyCollection<PckAsset> GetAssets()
```

Returns all assets.

---

### RemoveAsset

```
bool RemoveAsset(PckAsset asset)
```

Removes an asset.

---

### RemoveAll

```
void RemoveAll(Predicate<PckAsset> predicate)
```

Removes assets matching a predicate.

---

### InsertAsset

```
void InsertAsset(int index, PckAsset asset)
```

Inserts asset at position.

---

### IndexOfAsset

```
int IndexOfAsset(PckAsset asset)
```

Returns asset index.

---

# PckAsset

Namespace: `OMI.Formats.Pck`

Represents a file stored inside a `.pck` archive.

## Constructor

```
PckAsset(string filename, PckAssetType type)
```

---

## Properties

| Property        | Type           | Description                   |
| --------------- | -------------- | ----------------------------- |
| `Filename`      | `string`       | Asset path                    |
| `Type`          | `PckAssetType` | Asset type                    |
| `Data`          | `byte[]`       | Raw data                      |
| `Size`          | `int`          | Size of data                  |
| `PropertyCount` | `int`          | Number of metadata properties |

---

## Methods

### SetData

```
void SetData(byte[] data)
```

Sets raw asset data.

---

### AddProperty

```
void AddProperty(string name, string value)
void AddProperty<T>(string name, T value)
void AddProperty(KeyValuePair<string,string> property)
```

Adds a property.

---

### RemoveProperty

```
void RemoveProperty(string propertyName)
bool RemoveProperty(KeyValuePair<string,string> property)
```

Removes property.

---

### RemoveProperties

```
void RemoveProperties(string propertyName)
```

Removes all properties with the name.

---

### ClearProperties

```
void ClearProperties()
```

Removes all properties.

---

### HasProperty

```
bool HasProperty(string propertyName)
```

Checks if property exists.

---

### GetProperty

```
string GetProperty(string propertyName)
```

Returns property value.

---

### GetProperty

```
T GetProperty<T>(string propertyName, Func<string,T> parser)
```

Returns parsed value.

---

### TryGetProperty

```
bool TryGetProperty(string propertyName, out string value)
```

Python usage:

```
found, value = asset.TryGetProperty(name)
```

---

### GetMultipleProperties

```
KeyValuePair<string,string>[] GetMultipleProperties(string propertyName)
```

Returns all properties with the name.

---

### GetPropertyValues

```
string[] GetPropertyValues(string propertyName)
```

Returns values only.

---

### GetProperties

```
IReadOnlyList<KeyValuePair<string,string>> GetProperties()
```

Returns all properties.

---

### SetProperty

```
void SetProperty(string propertyName, string value)
void SetProperty(int index, KeyValuePair<string,string> property)
```

Updates property value.

---

### GetPropertyIndex

```
int GetPropertyIndex(KeyValuePair<string,string> property)
```

Returns property index.

---

# PckFileReader

Namespace: `OMI.Workers.Pck`

Reads `.pck` archives.

## Constructors

```
PckFileReader()
PckFileReader(ByteOrder byteOrder)
```

Default byte order: `BigEndian`.

---

## Methods

### FromFile

```
PckFile FromFile(string filename)
```

Reads `.pck` file from disk.

---

### FromStream

```
PckFile FromStream(Stream stream)
```

Reads `.pck` from a stream.

---

# PckFileWriter

Namespace: `OMI.Workers.Pck`

Writes `.pck` archives.

---

## Constructor

```
PckFileWriter(PckFile pckFile, ByteOrder byteOrder)
```

---

## Methods

### WriteToFile

```
void WriteToFile(string filename)
```

Writes archive to disk.

---

### WriteToStream

```
void WriteToStream(Stream stream)
```

Writes archive to a stream.

---

# EndiannessAwareBinaryReader

Namespace: `OMI`

Binary reader supporting configurable byte order.

Extends `.NET BinaryReader`.

## Constructors

```
EndiannessAwareBinaryReader(Stream)
EndiannessAwareBinaryReader(Stream, Encoding)
EndiannessAwareBinaryReader(Stream, Encoding, bool leaveOpen)
EndiannessAwareBinaryReader(Stream, ByteOrder)
EndiannessAwareBinaryReader(Stream, Encoding, ByteOrder)
EndiannessAwareBinaryReader(Stream, Encoding, bool leaveOpen, ByteOrder)
```

---

## Additional Methods

```
string ReadString(int length)
string ReadString(int length, Encoding encoding)
```

---

# EndiannessAwareBinaryWriter

Namespace: `OMI`

Binary writer supporting configurable byte order.

Extends `.NET BinaryWriter`.

---

## Constructors

```
EndiannessAwareBinaryWriter(Stream)
EndiannessAwareBinaryWriter(Stream, Encoding)
EndiannessAwareBinaryWriter(Stream, Encoding, bool leaveOpen)
EndiannessAwareBinaryWriter(Stream, ByteOrder)
EndiannessAwareBinaryWriter(Stream, Encoding, ByteOrder)
EndiannessAwareBinaryWriter(Stream, Encoding, bool leaveOpen, ByteOrder)
```

---

## Methods

```
void Write(short value, ByteOrder order)
void Write(int value, ByteOrder order)
void Write(long value, ByteOrder order)
void Write(float value, ByteOrder order)
```

### String writing

```
void WriteString(string s)
void WriteString(string s, Encoding encoding)
void WriteString(string s, int maxCapacity)
void WriteString(string s, int maxCapacity, Encoding encoding)
```

---

# IDataFormatReader

Namespace: `OMI.Workers`

Generic interface implemented by readers.

```
object FromStream(Stream stream)
object FromFile(string filename)
