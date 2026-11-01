# College Report Card Generator - PowerShell Implementation
# Reduces hallucinations through structured data validation and persistent context

param(
    [string]$Action = "generate",
    [string]$DataFile = "grades.csv",
    [string]$SyllabusFile = "syllabus.json",
    [string]$OutputDir = "output",
    [string]$TemplateFile = "template.html",
    [switch]$ValidateOnly,
    [switch]$ExportPdf
)

# ============================================================================
# MEMORY & CONTEXT MANAGEMENT
# ============================================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ContextFile = Join-Path $PSScriptRoot "context.json"
$CacheFile = Join-Path $PSScriptRoot "grade_cache.json"

# Load persistent context to prevent hallucination
function Load-Context {
    if (Test-Path $ContextFile) {
        $context = Get-Content $ContextFile | ConvertFrom-Json
        Write-Host "📋 Loaded context: $($context.Course) $($context.Term)" -ForegroundColor Cyan
        return $context
    }
    return @{
        Course = ""
        Term = ""
        GradingPolicy = @{}
        Rubric = @{}
        StudentCache = @{}
        LastProcessed = ""
    }
}

function Save-Context {
    param($Context)
    $Context.LastProcessed = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $Context | ConvertTo-Json -Depth 5 | Set-Content $ContextFile
}

# ============================================================================
# DATA VALIDATION (ANTI-HALLUCINATION)
# ============================================================================

function Load-GradeData {
    param($FilePath)
    if (-not (Test-Path $FilePath)) {
        Write-Error "Grade file not found: $FilePath"
        exit 1
    }
    $data = Import-Csv $FilePath
    Write-Host "📊 Loaded $($data.Count) student records" -ForegroundColor Green
    return $data
}

function Load-Syllabus {
    param($FilePath)
    if (-not (Test-Path $FilePath)) {
        Write-Error "Syllabus file not found: $FilePath"
        exit 1
    }
    $syllabus = Get-Content $FilePath | ConvertFrom-Json
    return $syllabus
}

function Validate-Grades {
    param($Data, $Syllabus)
    
    $errors = @()
    $warnings = @()
    
    foreach ($student in $Data) {
        # Check required fields
        $required = @('StudentID', 'StudentName', 'Assignments', 'Midterm', 'Final', 'Attendance')
        foreach ($field in $required) {
            if (-not $student.$field -or $student.$field -eq '') {
                $errors += "Student $($student.StudentID): Missing required field '$field'"
            }
        }
        
        # Validate numeric ranges
        $numericFields = @('Midterm', 'Final', 'Attendance')
        foreach ($field in $numericFields) {
            $value = [double]$student.$field
            if ($value -lt 0 -or $value -gt 100) {
                $errors += "Student $($student.StudentID): $field score $value out of range (0-100)"
            }
        }
        
        # Validate assignments
        $assignments = $student.Assignments -split ';' | ForEach-Object { [double]$_ }
        foreach ($score in $assignments) {
            if ($score -lt 0 -or $score -gt 100) {
                $errors += "Student $($student.StudentID): Assignment score $score out of range (0-100)"
            }
        }
        
        # Check weighting matches syllabus
        $totalWeight = ($Syllabus.Weights.Assignments + $Syllabus.Weights.Midterm + $Syllabus.Weights.Final + $Syllabus.Weights.Attendance)
        if ([math]::Abs($totalWeight - 1.0) -gt 0.01) {
            $warnings += "Syllabus weights sum to $totalWeight (should be 1.0)"
        }
    }
    
    if ($errors.Count -gt 0) {
        Write-Host "❌ VALIDATION ERRORS:" -ForegroundColor Red
        $errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    }
    if ($warnings.Count -gt 0) {
        Write-Host "⚠️ WARNINGS:" -ForegroundColor Yellow
        $warnings | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    }
    
    return @{ Errors = $errors; Warnings = $warnings; Valid = ($errors.Count -eq 0) }
}

# ============================================================================
# GRADE CALCULATION (DETERMINISTIC, NO HALLUCINATION)
# ============================================================================

function Calculate-FinalGrade {
    param($Student, $Syllabus)
    
    $weights = $Syllabus.Weights
    
    # Parse assignment scores
    $assignmentScores = $Student.Assignments -split ';' | ForEach-Object { [double]$_ }
    $assignmentAvg = ($assignmentScores | Measure-Object -Average).Average
    
    $midterm = [double]$Student.Midterm
    $final = [double]$Student.Final
    $attendance = [double]$Student.Attendance
    
    # Deterministic calculation - no AI involved
    $finalGrade = (
        ($assignmentAvg * $Syllabus.Weights.Assignments) +
        ($midterm * $Syllabus.Weights.Midterm) +
        ($final * $Syllabus.Weights.Final) +
        ($attendance * $Syllabus.Weights.Attendance)
    )
    
    return [math]::Round($finalGrade, 2)
}

function Get-LetterGrade {
    param($Score)
    if ($Score -ge 93) { return "A" }
    elseif ($Score -ge 90) { return "A-" }
    elseif ($Score -ge 87) { return "B+" }
    elseif ($Score -ge 83) { return "B" }
    elseif ($Score -ge 80) { return "B-" }
    elseif ($Score -ge 77) { return "C+" }
    elseif ($Score -ge 73) { return "C" }
    elseif ($Score -ge 70) { return "C-" }
    elseif ($Score -ge 67) { return "D+" }
    elseif ($Score -ge 63) { return "D" }
    elseif ($Score -ge 60) { return "D-" }
    else { return "F" }
}

# ============================================================================
# COMMENT GENERATION (TEMPLATE-BASED, NO HALLUCINATION)
# ============================================================================

function Generate-Comment {
    param($Student, $Grade, $LetterGrade, $Syllabus)
    
    $comments = @()
    
    # Attendance comment
    $attendance = [double]$Student.Attendance
    if ($attendance -ge 95) {
        $comments += "Excellent attendance ($attendance%). "
    } elseif ($attendance -ge 85) {
        $comments += "Good attendance ($attendance%). "
    } elseif ($attendance -ge 75) {
        $comments += "Attendance needs improvement ($attendance%). "
    } else {
        $comments += "Poor attendance ($attendance%) significantly impacted grade. "
    }
    
    # Performance comment
    $final = [double]$Student.FinalGrade
    if ($Student.FinalGrade -ge 90) {
        $comments += "Excellent mastery of course material. "
    } elseif ($Student.FinalGrade -ge 80) {
        $comments += "Strong understanding of course concepts. "
    } elseif ($Student.FinalGrade -ge 70) {
        $comments += "Satisfactory performance with room for improvement. "
    } elseif ($Student.FinalGrade -ge 60) {
        $comments += "Needs significant improvement. Consider tutoring. "
    } else {
        $comments += "Failed to meet minimum requirements. Must retake course. "
    }
    
    # Assignment consistency
    $assignments = $Student.Assignments -split ';' | ForEach-Object { [double]$_ }
    $assignmentStdDev = [math]::Sqrt(($assignmentScores | Measure-Object -Average -StandardDeviation).StandardDeviation)
    if ($assignmentStdDev -lt 10) {
        $comments += "Consistent assignment performance. "
    } elseif ($assignmentStdDev -gt 20) {
        $comments += "Inconsistent assignment performance. "
    }
    
    return $comments -join " "
}

# ============================================================================
# REPORT CARD GENERATION
# ============================================================================

function Generate-ReportCard {
    param($Student, $Syllabus, $Template)
    
    $Student.FinalGrade = Calculate-FinalGrade -Student $Student -Syllabus $Syllabus
    $LetterGrade = Get-LetterGrade -Score $Student.FinalGrade
    $Comment = Generate-Comment -Student $Student -Syllabus $Syllabus
    
    $report = @{
        StudentID = $Student.StudentID
        StudentName = $Student.StudentName
        Course = $Course
        Term = $Term
        FinalGrade = $Student.FinalGrade
        LetterGrade = $LetterGrade
        Assignments = $Student.Assignments
        Midterm = $Student.Midterm
        Final = $Student.Final
        Attendance = $Student.Attendance
        Comment = $Comment
        Date = Get-Date -Format "yyyy-MM-dd"
    }
    
    return $report
}

function Export-ReportCard {
    param($Report, $OutputDir, $TemplateFile, $ExportPdf)
    
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }
    
    $fileName = "$($Report.StudentID)_$($Report.Course)_$($Report.Term)_ReportCard.html"
    $outputPath = Join-Path $OutputDir $fileName
    
    # Read template
    $template = Get-Content $TemplateFile -Raw
    
    # Replace placeholders
    $html = $template
    $html = $html -replace '{{StudentName}}', $Report.StudentName
    $html = $html -replace '{{StudentID}}', $Report.StudentID
    $html = $html -replace '{{Course}}', $Report.Course
    $html = $html -replace '{{Term}}', $Report.Term
    $html = $html -replace '{{FinalGrade}}', $Report.FinalGrade
    $html = $html -replace '{{LetterGrade}}', $Report.LetterGrade
    $html = $html -replace '{{Comment}}', $Report.Comment
    $html = $html -replace '{{Date}}', $Report.Date
    $html = $html -replace '{{Assignments}}', $Report.Assignments
    $html = $html -replace '{{Midterm}}', $Report.Midterm
    $html = $html -replace '{{Final}}', $Report.Final
    $html = $html -replace '{{Attendance}}', $Report.Attendance
    
    $html | Set-Content $outputPath -Encoding UTF8
    Write-Host "✅ Generated: $outputPath" -ForegroundColor Green
    
    if ($ExportPdf) {
        # Convert to PDF using wkhtmltopdf or similar
        Write-Host "📄 PDF export not implemented - install wkhtmltopdf" -ForegroundColor Yellow
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Load context
$context = Load-Context

# Parse syllabus
$Syllabus = Load-Syllabus -FilePath $SyllabusFile
$Course = $Syllabus.Course
$Term = $Syllabus.Term

# Load and validate grades
$GradeData = Load-GradeData -FilePath $DataFile
$Validation = Validate-Grades -Data $GradeData -Syllabus $Syllabus

if (-not $Validation.Valid) {
    Write-Error "Grade validation failed. Fix errors before proceeding."
    exit 1
}

if ($ValidateOnly) {
    Write-Host "✅ Validation passed - no errors found" -ForegroundColor Green
    exit 0
}

# Update context
$Context.Course = $Course
$Context.Term = $Term
$Context.GradingPolicy = $Syllabus.Weights
$Context.Rubric = $Syllabus.Rubric
$Context.LastProcessed = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Save-Context -Context $Context

# Process each student
$Reports = @()
foreach ($Student in $GradeData) {
    Write-Host "Processing $($Student.StudentName) ($($Student.StudentID))..." -ForegroundColor Cyan
    
    $Report = Generate-ReportCard -Student $Student -Syllabus $Syllabus
    $Reports += $Report
    
    # Cache student data for memory
    $Context.StudentCache[$Student.StudentID] = @{
        Name = $Student.StudentName
        FinalGrade = $Student.FinalGrade
        LetterGrade = $LetterGrade
        LastGenerated = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    Save-Context -Context $Context
    
    # Export individual report
    Export-ReportCard -Report $Student -OutputDir $OutputDir -TemplateFile $TemplateFile -ExportPdf $ExportPdf
}

# Generate summary
$summary = @{
    Course = $Course
    Term = $Term
    TotalStudents = $Reports.Count
    AverageGrade = ($Reports | Measure-Object -Property FinalGrade -Average).Average
    GradeDistribution = $Reports | Group-Object LetterGrade | Sort-Object Name | ForEach-Object { @{ Grade = $_.Name; Count = $_.Count } }
    Date = Get-Date -Format "yyyy-MM-dd"
}

$summaryPath = Join-Path $OutputDir "summary_${Course}_${Term}.json"
$summary | ConvertTo-Json -Depth 5 | Set-Content $SummaryPath

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "REPORT CARDS GENERATED: $($Reports.Count) students" -ForegroundColor Green
Write-Host "Average Grade: $([math]::Round($summary.AverageGrade, 2))" -ForegroundColor Green
Write-Host "Output: $OutputDir" -ForegroundColor Green
Write-Host "Summary: $SummaryPath" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green