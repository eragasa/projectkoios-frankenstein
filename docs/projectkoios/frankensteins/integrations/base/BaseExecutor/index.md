# `BaseExecutor`

`BaseExecutor[RequestT, ResultT]` is the common abstract interface for an
application integration.

## Public contract

- `application_name`: stable external-application identifier.
- `execute(request, *, workspace)`: execute one typed request in an explicit
  workspace and return the integration-specific typed result.

The base does not select or discover an executable, create a workspace, invoke a
process, or interpret calculator output. Concrete executors must use argument
arrays rather than shell command strings, operate in an isolated explicit
workspace, bound runtime and captured output, require declared result artifacts,
and keep completion distinct from numerical verification and scientific
validation.

Importing or subclassing `BaseExecutor` does not itself authorize an external
run. Concrete integrations must receive execution authority and local resources
through their own explicit runtime boundary.
