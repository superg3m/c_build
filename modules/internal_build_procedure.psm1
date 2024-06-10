class BuildProcedure {
    [string]$name
    [bool]$should_build_procedure

    [string]$output_name


    Person ([string]$firstName, [string]$lastName, [int]$age) {
        $this.FirstName = $firstName
        $this.LastName = $lastName
        $this.Age = $age
    }

    [void]DisplayInfo() {
        Write-Host "Name: $($this.FirstName) $($this.LastName), Age: $($this.Age)"
    }
}