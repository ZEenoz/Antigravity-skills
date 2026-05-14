# JavaFX Enterprise Coding Standards

## Architecture
- FXML/View: layout only.
- Controller: UI events and view state only.
- Service: business rules.
- Repository/API Client: persistence or remote calls.
- Model/DTO/ViewModel: data state.

## FXML
- `fx:controller` must match controller class.
- `fx:id` must match `@FXML` fields.
- `onAction` must match controller methods.
- Prefer CSS classes over inline styles.

## Controller
- Keep `initialize()` short and focused.
- Do not block JavaFX Application Thread.
- Validate input before service calls.
- Show clear user feedback.
- Do not put SQL/business rules directly in controller.

## JavaFX Threading
- Use `Task`/`Service` for long-running work.
- Update UI on FX Application Thread.
- Disable controls during save/load if needed.

## TableView
- Use `ObservableList`.
- Configure columns once.
- Handle empty selection.
- Refresh after CRUD operations.

## Enterprise Quality
- User-friendly errors.
- No secrets in logs.
- Minimal diff.
- Clear run/debug commands.
