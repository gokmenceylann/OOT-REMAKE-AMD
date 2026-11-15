$ErrorActionPreference = 'Stop'
$measure = Join-Path (Split-Path $PSScriptRoot) 'scripts/Measure-FrameTimes.ps1'
$fixture = Join-Path ([IO.Path]::GetTempPath()) ("oot-frame-times-" + [Guid]::NewGuid() + ".csv")
try {
    @('frame,time_s,frametime_ms', '0,0,0', '1,0.016,16', '2,0.066,50',
        '3,0.166,100', '4,0.367,201') | Set-Content -LiteralPath $fixture -Encoding ascii
    $result = & $measure -CsvPath $fixture
    if ($result.SampleCount -ne 4 -or $result.P50Ms -ne 50 -or $result.P95Ms -ne 201 -or
        $result.P99Ms -ne 201 -or $result.MaxMs -ne 201 -or $result.Over33Point3Ms -ne 3 -or
        $result.Over50Ms -ne 2 -or $result.Over100Ms -ne 1) {
        throw 'Unexpected frame-time distribution.'
    }
    $window = & $measure -CsvPath $fixture -SkipSeconds 0.06 -DurationSeconds 0.20
    if ($window.SampleCount -ne 2 -or $window.MaxMs -ne 100 -or $window.Over100Ms -ne 0) {
        throw 'A spike outside the requested window entered the report.'
    }
    'Frame-time distribution and spike count tests passed.'
} finally {
    if (Test-Path -LiteralPath $fixture) { Remove-Item -LiteralPath $fixture }
}
