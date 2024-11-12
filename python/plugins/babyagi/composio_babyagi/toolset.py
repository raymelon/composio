from ast import List
import types
import typing as t
from inspect import Signature

import babyagi
import typing_extensions as te
from babyagi.functionz.core.framework import func

from composio import Action, ActionType, AppType, TagType
from composio.tools.toolset import ComposioToolSet as BaseComposioToolSet 
from composio.tools.toolset import ProcessorsType
from composio.utils.shared import (
    get_signature_format_from_schema_params,
    json_schema_to_model,
)

class ComposioToolSet(
    BaseComposioToolSet,
    runtime="babyagi",
    description_char_limit=1024,
):
    """
    Composio toolset for babyagi framework.
    """
    def _wrap_action(
        self,
        action: str,
        description: str,
        schema_params: t.Dict,
        entity_id: t.Optional[str] = None,
    ):
        def wrapped_function(text) -> dict:
            """Wrapper function for composio action."""
            return self.execute_action(
                action=Action(value=action),
                params={},
                text=text,
                entity_id=entity_id or self.entity_id,
            )

        # Register the wrapped_function with the action name
        babyagi.register_function(func=wrapped_function)

        action_func = types.FunctionType(
            wrapped_function.__code__,
            globals=globals(),
            name=wrapped_function.__name__,  # Use the name of the wrapped function
            closure=wrapped_function.__closure__,
        )
        action_func.__signature__ = Signature(  # type: ignore
            parameters=get_signature_format_from_schema_params(
                schema_params=schema_params
            )
        )

        action_func.__doc__ = description

        return action_func

    def _wrap_tool(
        self,
        schema: t.Dict[str, t.Any],
        entity_id: t.Optional[str] = None,
    ) -> types.FunctionType:
        """Wraps composio tool as babyagi function object."""
        action = schema["name"]
        description = schema["description"]
        schema_params = schema["parameters"]
        
        return self._wrap_action(
            action=action,
            description=description,
            schema_params=schema_params,
            entity_id=entity_id,
        )
    
    @te.deprecated("Use `ComposioToolSet.get_tools` instead")
    def get_actions(
        self,
        actions: t.Sequence[ActionType],
        entity_id: t.Optional[str] = None,
    ) -> t.List[types.FunctionType]:
        """
        Get composio tools wrapped as babyagi functions.

        :param actions: List of actions to wrap
        :param entity_id: Entity ID to use for executing function calls.

        :return: Composio tools wrapped as `FunctionType` objects
        """
        return self.get_tools(actions=actions, entity_id=entity_id)

    def get_tools(
        self,
        actions: t.Optional[t.Sequence[ActionType]] = None,
        apps: t.Optional[t.Sequence[AppType]] = None,
        tags: t.Optional[t.List[TagType]] = None,
        entity_id: t.Optional[str] = None,
        *,
        processors: t.Optional[ProcessorsType] = None,
        check_connected_accounts: bool = True,
    ) -> t.List[types.FunctionType]:
        """
        Get composio tools wrapped as babyagi functions.

        :param actions: List of actions to wrap
        :param apps: List of apps to wrap
        :param tags: Filter the apps by given tags
        :param entity_id: Entity ID for the function wrapper
        :param processors: Optional processors to merge
        :param check_connected_accounts: Whether to check connected accounts

        :return: Composio tools wrapped as `FunctionType` objects
        """
        self.validate_tools(apps=apps, actions=actions, tags=tags)
        if processors is not None:
            self._merge_processors(processors)
            
        tools = [
            self._wrap_tool(
                schema=tool.model_dump(exclude_none=True),
                entity_id=entity_id or self.entity_id,
            )
            for tool in self.get_action_schemas(
                actions=actions,
                apps=apps,
                tags=tags,
                check_connected_accounts=check_connected_accounts,
            )
        ]
        
        # Register tools with babyagi
        for tool in tools:
            if not hasattr(tool, '_is_registered'):
                babyagi.register_function(func=tool)
                tool._is_registered = True  # type: ignore
        return tools