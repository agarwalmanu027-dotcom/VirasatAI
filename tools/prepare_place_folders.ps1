param([string]$ProjectRoot = 'C:\Desktop\VirasatAI')

$ErrorActionPreference = 'Stop'
$rootPath = [IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\', '/')
if ($rootPath -ne 'C:\Desktop\VirasatAI') { throw 'Unexpected workspace root.' }
$rootPrefix = $rootPath + [IO.Path]::DirectorySeparatorChar
$catalogPath = Join-Path $rootPath '06_Database\JSON\monuments_places_catalog.json'
$catalog = Get-Content -LiteralPath $catalogPath -Raw -Encoding utf8 | ConvertFrom-Json -Depth 60
if (@($catalog.main_monuments).Count -ne 20) { throw 'Expected 20 main groups.' }
if (@($catalog.main_monuments | ForEach-Object { $_.nearby_places }).Count -ne 200) { throw 'Expected 200 nearby entries.' }
foreach ($main in $catalog.main_monuments) {
    if (@($main.nearby_places).Count -ne 10) { throw ('Expected 10 nearby entries for ' + $main.display_name) }
}

$preparedNearbyReadmes = @(
    '01_Data\Taj_Mahal\Nearby_Heritage\README.txt',
    '02_Images\Taj_Mahal\Nearby_Heritage\README.txt',
    '03_Scripts\Taj_Mahal\Nearby_Heritage\README.txt',
    '04_Audio\Taj_Mahal\Nearby_Heritage\README.txt'
) | ForEach-Object { Join-Path $rootPath $_ }
$protectedFiles = @(
    foreach ($section in @('01_Data', '02_Images', '03_Scripts', '04_Audio')) {
        foreach ($item in Get-ChildItem -LiteralPath (Join-Path $rootPath $section) -File -Recurse) {
            if ($item.FullName -notin $preparedNearbyReadmes) {
                [PSCustomObject]@{ path = $item.FullName; sha256 = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash }
            }
        }
    }
)

$expectedDirectories = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$createdDirectoryCount = 0
$createdReadmeCount = 0

function Get-SafePath([string]$RelativePath) {
    if ([IO.Path]::IsPathRooted($RelativePath)) { throw 'Expected a relative catalog path.' }
    $fullPath = [IO.Path]::GetFullPath([IO.Path]::Combine($rootPath, $RelativePath.Replace('/', '\')))
    if (-not $fullPath.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Path leaves the workspace.' }
    return $fullPath
}

function Ensure-Directory([string]$RelativePath) {
    $fullPath = Get-SafePath $RelativePath
    if (-not [IO.Directory]::Exists($fullPath)) {
        if ([IO.File]::Exists($fullPath)) { throw ('A file blocks directory creation: ' + $RelativePath) }
        [void][IO.Directory]::CreateDirectory($fullPath)
        $script:createdDirectoryCount++
    }
    [void]$expectedDirectories.Add($fullPath)
}

function Write-NewText([string]$RelativePath, [string]$Text) {
    $fullPath = Get-SafePath $RelativePath
    if ([IO.File]::Exists($fullPath)) { return }
    if ([IO.Directory]::Exists($fullPath)) { throw ('A directory blocks file creation: ' + $RelativePath) }
    [void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($fullPath))
    [IO.File]::WriteAllText($fullPath, $Text + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    if ($RelativePath.EndsWith('/README.txt')) { $script:createdReadmeCount++ }
}

function Prepare-Place($Place, [bool]$IsMain, [string]$ParentName) {
    foreach ($section in @('data', 'images', 'scripts', 'audio')) {
        Ensure-Directory $Place.paths.$section
    }
    foreach ($category in @('Basic_Info', 'Facts', 'Story_Data', 'Sources')) {
        Ensure-Directory ($Place.paths.data + '/' + $category)
    }

    if ($IsMain -and $Place.id -eq 'taj_mahal') {
        $imageCategories = @('Front', 'Back_Yamuna', 'East', 'West', 'North', 'South', 'Aerial', 'Dome', 'Minarets', 'Interior', 'Jali', 'Pietra_Dura', 'Calligraphy', 'Mosque', 'Jawab', 'Garden', 'Image_Sources')
    } elseif ($IsMain) {
        $imageCategories = @('Front', 'Back', 'East', 'West', 'North', 'South', 'Aerial', 'Details', 'Surroundings', 'Image_Sources')
    } else {
        $imageCategories = @('Overview', 'Different_Views', 'Details', 'Surroundings', 'Image_Sources')
    }
    foreach ($category in $imageCategories) {
        Ensure-Directory ($Place.paths.images + '/' + $category)
    }
    foreach ($language in @('English', 'Hindi', 'Voice_Directions')) {
        Ensure-Directory ($Place.paths.scripts + '/' + $language)
    }
    foreach ($language in @('English', 'Hindi')) {
        Ensure-Directory ($Place.paths.audio + '/' + $language)
    }

    $typeLabel = if ($IsMain) { 'Main monument group' } else { 'Nearby / less-famous place' }
    $parentLine = if ($IsMain) { '' } else { 'Parent main monument: ' + $ParentName }
    $statusLine = if ($Place.id -eq 'taj_mahal') { 'Existing Taj Mahal files are preserved.' } else { 'Status: Folders prepared. Verified facts, master scripts, audio and images are not yet added.' }
    $lines = @(
        'VIRASATAI - PLACE CONTENT',
        ('Selected name: ' + $Place.display_name),
        ('Place ID: ' + $Place.id),
        ('Type: ' + $typeLabel),
        $parentLine,
        '',
        $statusLine,
        '',
        'Basic_Info: name, verified location, background and architecture.',
        'Facts: verified facts with references.',
        'Story_Data: selected facts for a connected heritage story.',
        'Sources: official government, ASI, UNESCO or official tourism references.',
        '',
        ('Display images: ' + $Place.paths.images),
        ('English/Hindi scripts and voice directions: ' + $Place.paths.scripts),
        ('English/Hindi audio: ' + $Place.paths.audio),
        '',
        'The place name and parent association come from the user-selected list.',
        'Distances, travel time, historical details and site identity still require verification.',
        'Application display images remain separate from 05_AI_Dataset.'
    )
    Write-NewText ($Place.paths.data + '/README.txt') ($lines -join [Environment]::NewLine)
}

foreach ($main in $catalog.main_monuments) {
    Prepare-Place $main $true ''
    foreach ($section in @('data', 'images', 'scripts', 'audio')) {
        $nearbyRoot = $main.paths.$section + '/Nearby_Heritage'
        Ensure-Directory $nearbyRoot
        $readme = @(
            'VIRASATAI - NEARBY / LESS-FAMOUS PLACES',
            ('Main monument: ' + $main.display_name),
            'The user-selected list contains ten entries for this group.',
            'Each entry has its own folder. Names and order are recorded in the main catalog.',
            '',
            'Catalog: 06_Database/JSON/monuments_places_catalog.json',
            ('Nearby index: ' + $main.paths.data + '/Nearby_Heritage/nearby_places_index.json'),
            '',
            'Status: Place folders prepared. Source research, stories and new images are pending.',
            'Nearby is the user-selected association; distance and travel time are not yet verified.'
        ) -join [Environment]::NewLine
        $readmeRelativePath = $nearbyRoot + '/README.txt'
        $readmeFullPath = Get-SafePath $readmeRelativePath
        if ($readmeFullPath -in $preparedNearbyReadmes) {
            [IO.File]::WriteAllText($readmeFullPath, $readme + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
        } else {
            Write-NewText $readmeRelativePath $readme
        }
    }
    foreach ($nearby in $main.nearby_places) {
        Prepare-Place $nearby $false $main.display_name
    }
    $index = [ordered]@{
        parent_monument_id = $main.id
        parent_monument_name = $main.display_name
        selection_source = 'User-supplied table'
        nearby_entry_count = 10
        places = @($main.nearby_places)
    }
    Write-NewText ($main.paths.data + '/Nearby_Heritage/nearby_places_index.json') ($index | ConvertTo-Json -Depth 30)
}

Ensure-Directory '06_Database/JSON'
Ensure-Directory '06_Database/SQL'

$missingDirectories = @($expectedDirectories | Where-Object { -not [IO.Directory]::Exists($_) })
if ($missingDirectories.Count -gt 0) { throw ('Missing directories: ' + ($missingDirectories -join ', ')) }
$changedProtectedFiles = @(
    foreach ($file in $protectedFiles) {
        if (-not [IO.File]::Exists($file.path)) { $file.path }
        elseif ((Get-FileHash -LiteralPath $file.path -Algorithm SHA256).Hash -ne $file.sha256) { $file.path }
    }
)
if ($changedProtectedFiles.Count -gt 0) { throw ('Existing asset changed: ' + ($changedProtectedFiles -join ', ')) }

$report = [ordered]@{
    recorded_on = '2026-10-07'
    task = 'Prepare folders for the supplied main-monument and nearby-place list'
    main_groups = 20
    nearby_entries = 200
    place_records = 220
    expected_directories_checked = $expectedDirectories.Count
    new_directories_created = $createdDirectoryCount
    new_place_and_group_readmes_created = $createdReadmeCount
    protected_existing_assets_checked = $protectedFiles.Count
    changed_protected_assets = $changedProtectedFiles
    taj_mahal_display_images = @(Get-ChildItem -LiteralPath (Join-Path $rootPath '02_Images\Taj_Mahal') -File -Recurse | Where-Object { $_.Extension -match '^\.(jpg|jpeg|png|webp)$' }).Count
    longest_expected_path_characters = ($expectedDirectories | ForEach-Object { $_.Length } | Measure-Object -Maximum).Maximum
    missing_directories = $missingDirectories
    content_stage = 'Folders prepared; verified details, new scripts, audio and new images pending'
    protected_assets = $protectedFiles
}
$reportPath = Get-SafePath '06_Database/JSON/folder_preparation_report.json'
[IO.File]::WriteAllText($reportPath, ($report | ConvertTo-Json -Depth 12) + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
[PSCustomObject]$report | Select-Object recorded_on, main_groups, nearby_entries, place_records, expected_directories_checked, new_directories_created, protected_existing_assets_checked, taj_mahal_display_images, longest_expected_path_characters, content_stage | ConvertTo-Json
