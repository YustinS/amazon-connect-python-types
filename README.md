# Amazon Connect Python Types

This repository provides type definitions for Amazon Connect services in Python. These are intended to be used in validation scenarios and development environments to ensure type safety and improve code quality when working with Amazon Connect.
In particular, this repo contains type definitions that otherwise don't exist in `boto3` by default, or may otherwise be useful to validate.

## Proficiency Routing

The type definitions for Proficiency Routing are based on the [Amazon Connect Proficiency Routing documentation](https://docs.aws.amazon.com/connect/latest/adminguide/proficiency-routing.html), and the provided [Lambda sample references](https://docs.aws.amazon.com/connect/latest/adminguide/set-routing-criteria.html#set-routing-criteria-sample-lambda-function)
Since these inputs require relatively complex structures, having pydantic definitions can help ensure that they are constructed correctly, and also can allow for more certainty when providing inputs or generating a a response, such as in an API scenario to manage a large assortment of proficiencies.

### Usage

To use this type definition, you should add the code files as relevant to your project.
For example, to use the `ProficiencyRoutingPayload` type definition in your code, you can do

```python
    my_proficiency_payload = {
        # your proficiency payload data here
    }
    try:
        validated_payload = ProficiencyRoutingPayload.model_validate(my_proficiency_payload)
    except ValidationError as e:
        print("Invalid proficiency payload:", e)
```

## Contact Flow Event

This type definition is not strictly intended for usage in production code, as the input is provided from Amazon Connect and should be consistent without much further maniupulation (if any is required its more likely to be around ensuring expected parameters or attributes exist to be used).
Instead, this is more intended to be used in development environments to help ensure that code working with Contact Flow Event data is correctly handling the expected structure.
Importantly, this may not include all `enum` values. Notably, this doesn't currently include any email channel related values.

## Development

These repo uses [uv](https://uv.dev/) to manage the development environment and dependencies.
To set up the development environment, run:

```sh
make install
```

To run the unit tests with code coverage, run:

```sh
make test
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
